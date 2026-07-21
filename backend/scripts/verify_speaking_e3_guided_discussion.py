"""Verify Speaking E3 guided discussion runtime.

Usage:
  python -u scripts/verify_speaking_e3_guided_discussion.py
  $env:SPEAKING_VERIFY_SKIP_NESTED_REGRESSIONS='1'
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

PASS = 0
FAIL = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  OK  {name}", flush=True)
    else:
        FAIL += 1
        suffix = f" — {detail}" if detail else ""
        print(f" FAIL {name}{suffix}", flush=True)


def sample_constraints() -> dict:
    return {
        "skill": "speaking",
        "official_cefr": "A2",
        "learning_stage": 1,
        "mission_id": "mission_e3",
        "mission_kind": "guided_practice",
        "execution_mode": "controlled_response",
        "evidence_intent": "formative",
        "blueprint_id": "bp_e3",
        "blueprint_hash": "hash_e3",
        "learning_focus": "ordering coffee",
        "objectives": ["Order politely"],
        "vocabulary_ids": ["v_coffee", "v_please"],
        "vocabulary_surface_forms": ["coffee", "please"],
        "grammar_topic_ids": [],
        "teaching_block_specs": [
            {"block_id": "tb1", "kind": "explanation", "target_skill_ids": [], "max_len": 160}
        ],
        "weak_skill_labels": [],
        "difficulty": "standard",
        "scenario_type": "cafe",
        "input_material_kind": "story",
        "lesson_length_band": "short",
        "mini_practice_task_id": "task_e3",
        "reflection_requirements": {"prompt_count": 2},
        "locale": "en",
    }


def test_e3_units() -> None:
    print("\n--- E3 guided discussion units ---", flush=True)
    from app.services.language_educational_package.pipeline import process_package_generation
    from app.services.language_speaking_educational_package.constraint_builder import (
        build_speaking_package_constraints,
    )
    from app.services.language_speaking_educational_package.template_author import (
        AUTHOR_PROVIDER_TEMPLATE,
        author_package_json_template,
    )
    from app.services.language_speaking_discussion.engine import (
        DiscussionRuntimeError,
        advance_discussion_step,
        get_discussion_view,
        open_discussion,
        submit_discussion_response,
    )
    from app.services.language_speaking_discussion.guards import sanitize_tutor_text
    from app.services.language_speaking_discussion.storage import SPEAKING_DISCUSSION_RUNTIME_KEY
    from app.services.language_speaking_discussion.types import DiscussionPhase
    from app.services.language_speaking_lesson_runtime.types import (
        LessonRuntimeSection,
        LessonRuntimeState,
    )
    from app.services.language_speaking import ownership as owning

    constraints = build_speaking_package_constraints(sample_constraints())
    gen = process_package_generation(
        constraints,
        author_package_json_template(constraints),
        author_provider=AUTHOR_PROVIDER_TEMPLATE,
    )
    check("1. frozen package ready", gen.success and gen.package is not None)
    package = gen.package
    assert package is not None
    frozen_copy = package.to_dict()
    steps_n = len(package.discussion.steps)
    check("2. discussion steps authored", steps_n >= 4)

    item = SimpleNamespace(
        id=77,
        body_json={
            "educational_package": package.to_dict(),
            "package_id": package.package_id,
            "immutable": True,
        },
    )
    lesson_state = LessonRuntimeState(
        package_id=package.package_id,
        content_item_id=77,
        constraints_fingerprint=package.constraints_fingerprint,
        content_fingerprint=package.content_fingerprint,
        current_section=LessonRuntimeSection.completed,
        completed_sections=["introduction", "reading", "vocabulary", "teaching", "mini_practice", "completed"],
        mini_practice_prep_done=True,
        ready_for_discussion=True,
    )
    row = SimpleNamespace(
        promotion_readiness_json={
            "speaking_lesson_runtime": lesson_state.to_dict(),
        }
    )

    async def fake_get(*_a, **_k):
        return item

    async def fake_lock(*_a, **_k):
        return row

    async def _run() -> None:
        fake_db = SimpleNamespace()
        with (
            patch(
                "app.services.language_speaking_discussion.engine.get_package_item_by_id",
                new=fake_get,
            ),
            patch(
                "app.services.language_speaking_discussion.engine._lock_row",
                new=fake_lock,
            ),
            patch(
                "app.services.language_speaking_discussion.engine.flag_modified",
                lambda *_a, **_k: None,
            ),
            patch(
                "app.services.language_speaking_discussion.claude_tutor.is_claude_configured",
                return_value=False,
            ),
        ):
            # Gate without lesson ready
            bad_row = SimpleNamespace(promotion_readiness_json={})
            async def lock_bad(*_a, **_k):
                return bad_row
            with patch(
                "app.services.language_speaking_discussion.engine._lock_row",
                new=lock_bad,
            ):
                denied = False
                try:
                    await open_discussion(fake_db, student_id=1, language_id=1)
                except DiscussionRuntimeError as exc:
                    denied = exc.code in {"lesson_required", "lesson_not_ready"}
                check("3. blocks open without lesson ready", denied)

            view = await open_discussion(
                fake_db, student_id=1, language_id=1, package_id=package.package_id
            )
            check("4. open waiting_for_student", view.state.phase == DiscussionPhase.waiting_for_student)
            check("5. first step prompt present", bool(view.current_step and view.current_step.get("prompt")))
            check("6. not completed", not view.state.completed)

            view = await submit_discussion_response(
                fake_db,
                student_id=1,
                language_id=1,
                student_response="I would like a coffee please.",
            )
            check("7. submit returns assistant reply", bool(view.latest_assistant and view.latest_assistant.get("utterance")))
            check("8. student turn stored", any(t.role == "student" for t in view.state.turns))
            check(
                "9. template provider used",
                view.provider in {"template_fallback", "claude-discussion-tutor", ""},
            )

            # Advance through remaining steps
            for i in range(steps_n):
                # ensure answered
                if package.discussion.steps[min(i, steps_n - 1)].step_id not in view.state.answered_step_ids:
                    view = await submit_discussion_response(
                        fake_db,
                        student_id=1,
                        language_id=1,
                        student_response=f"Here is my longer answer number {i} about the cafe.",
                    )
                view = await advance_discussion_step(fake_db, student_id=1, language_id=1)
                if view.state.completed:
                    break
            check("10. discussion completed", view.state.completed)
            check("11. ready_for_alex set", view.state.ready_for_alex)

            resumed = await get_discussion_view(fake_db, student_id=1, language_id=1)
            check("12. resume completed", resumed.state.completed)
            check(
                "13. memory key present",
                SPEAKING_DISCUSSION_RUNTIME_KEY in (row.promotion_readiness_json or {}),
            )

            check(
                "14. frozen package unchanged",
                item.body_json["educational_package"] == frozen_copy,
            )

    asyncio.run(_run())

    # Guards strip CEFR / promotion language
    cleaned = sanitize_tutor_text("Your CEFR is B1 and you are promoted with a high score.")
    check("15. guard strips CEFR/promotion/score", "CEFR" not in cleaned and "promot" not in cleaned.lower())

    pkg = BACKEND / "app/services/language_speaking_discussion"
    text = "\n".join(p.read_text(encoding="utf-8") for p in pkg.glob("*.py"))
    check("16. no evaluation runtime import", "language_speaking_evaluation_runtime" not in text)
    check("17. no official promotion import", "official_promotion" not in text)
    check("18. no author_pipeline import", "author_pipeline" not in text)
    check("19. no alex_context import", "alex_context" not in text)
    check("19b. Claude tutor module present", (pkg / "claude_tutor.py").is_file())
    check("19c. GPT tutor module removed", not (pkg / "gpt_tutor.py").is_file())
    check("19d. no OpenAI chat completions in E3", "api.openai.com" not in text)
    check(
        "19e. no Scene Practice / Alex coupling",
        "language_speaking_live_bridge" not in text and "alex_context" not in text,
    )

    check("20. ownership registers discussion", "language_speaking_discussion" in owning.PACKAGE_OWNERSHIP)
    deps = owning.ALLOWED_PACKAGE_DEPENDENCIES["language_speaking_discussion"]
    check("21. depends on educational_package", "language_speaking_educational_package" in deps)
    check("22. depends on lesson_runtime", "language_speaking_lesson_runtime" in deps)
    check("22b. may use audio_frontend for STT/TTS", "language_speaking_audio_frontend" in deps)
    check("23. layer experience", owning.PACKAGE_LAYER.get("language_speaking_discussion") == "experience")

    api = (BACKEND / "app/api/language_speaking_discussion.py").read_text(encoding="utf-8")
    router = (BACKEND / "app/api/router.py").read_text(encoding="utf-8")
    check("24. discussion API routes", "/discussion" in api and "/submit" in api)
    check("24b. voice submit route", "/submit-voice" in api)
    check("25. router registers E3", "language_speaking_discussion" in router)
    check("26. no evaluation endpoints", "evaluation" not in api.lower())

    fe_api = BACKEND.parent / "src/api/speakingDiscussion.js"
    fe_ui = BACKEND.parent / "src/components/language/SpeakingGuidedDiscussion.vue"
    fe_view = BACKEND.parent / "src/views/student/languages/StudentLanguageSpeakingView.vue"
    check("27. FE discussion API", fe_api.is_file())
    check("28. FE discussion UI", fe_ui.is_file())
    fe_api_text = fe_api.read_text(encoding="utf-8")
    fe_view_text = fe_view.read_text(encoding="utf-8")
    check("29. FE voice submit client", "submit-voice" in fe_api_text or "submitSpeakingDiscussionVoice" in fe_api_text)
    check("30. FE shell has no Scene Practice tab", 'value="bridge"' not in fe_view_text)
    check("31. FE shell has no SpeakingLiveBridge", "SpeakingLiveBridge" not in fe_view_text)
    check("32. FE discussion hands off to Alex", "start-alex" in fe_view_text or "goLivePrepared" in fe_view_text)


def run_flat_verifier(label: str, script: str, timeout_s: int = 180) -> bool:
    env = {
        **os.environ,
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
        "PYTHONUNBUFFERED": "1",
        "SPEAKING_VERIFY_SKIP_NESTED_REGRESSIONS": "1",
    }
    log_path = BACKEND / "scripts" / f"_flat_{Path(script).stem}.log"
    with open(log_path, "w", encoding="utf-8", errors="replace") as logf:
        proc = subprocess.Popen(
            [sys.executable, "-u", str(BACKEND / "scripts" / script)],
            cwd=str(BACKEND),
            stdout=logf,
            stderr=subprocess.STDOUT,
            env=env,
        )
        try:
            proc.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            proc.kill()
            print(f"TIMEOUT after {timeout_s}s: {script}", flush=True)
            return False
    ok = proc.returncode == 0
    print(f"  {'OK' if ok else 'FAIL'}  {label} (exit={proc.returncode})", flush=True)
    if not ok:
        try:
            print(log_path.read_text(encoding="utf-8", errors="replace")[-2500:], flush=True)
        except OSError:
            pass
    return ok


FLAT_REGRESSION_CHAIN: tuple[tuple[str, str], ...] = (
    ("S0", "verify_speaking_s0_architecture.py"),
    ("S9", "verify_speaking_s9_adaptive_journey.py"),
    ("S10", "verify_speaking_s10_educational_missions.py"),
    ("S10.1", "verify_speaking_s101_mission_stabilization.py"),
    ("S11", "verify_speaking_s11_attempt_lineage.py"),
    ("S12", "verify_speaking_s12_journey_read_model.py"),
    ("S13", "verify_speaking_s13_live_budget.py"),
    ("S14", "verify_speaking_s14_alex_context_identity.py"),
    ("S15", "verify_speaking_s15_stage_signals.py"),
    ("S16", "verify_speaking_s16_transition_gate.py"),
    ("S17", "verify_speaking_s17_promotion_readiness.py"),
    ("S18", "verify_speaking_s18_promotion_assessment_blueprint.py"),
    ("S19", "verify_speaking_s19_promotion_assessment_execution.py"),
    ("S20", "verify_speaking_s20_official_promotion.py"),
    ("E1", "verify_speaking_e1_learning_package.py"),
    ("E2", "verify_speaking_e2_lesson_runtime.py"),
)


def main() -> int:
    skip = os.environ.get("SPEAKING_VERIFY_SKIP_NESTED_REGRESSIONS") == "1"
    if not skip:
        print("=== Speaking E3 FLAT regression runner ===\n", flush=True)
        for label, script in FLAT_REGRESSION_CHAIN:
            if not run_flat_verifier(label, script):
                print(f"\n=== STOPPED: flat regression failed at {label} ===", flush=True)
                return 1
        print("\n=== FLAT E3 (this process) ===", flush=True)

    print("=== Speaking E3 guided discussion verifier ===\n", flush=True)
    test_e3_units()
    print(f"\n=== E3 units: {PASS} passed, {FAIL} failed ===", flush=True)
    if FAIL:
        return 1
    if not skip:
        print("\n=== RESULT: all flat regressions + E3 units passed ===", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
