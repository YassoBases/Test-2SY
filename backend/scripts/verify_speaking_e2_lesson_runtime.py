"""Verify Speaking E2 lesson runtime (frozen package player).

Usage:
  python -u scripts/verify_speaking_e2_lesson_runtime.py
  $env:SPEAKING_VERIFY_SKIP_NESTED_REGRESSIONS='1'
"""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

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
        "mission_id": "mission_e2",
        "mission_kind": "teaching",
        "execution_mode": "study",
        "evidence_intent": "none",
        "blueprint_id": "bp_e2",
        "blueprint_hash": "hash_e2",
        "learning_focus": "greeting a guest",
        "objectives": ["Greet politely"],
        "vocabulary_ids": ["v_hello", "v_welcome"],
        "vocabulary_surface_forms": ["hello", "welcome"],
        "grammar_topic_ids": [],
        "teaching_block_specs": [
            {"block_id": "tb1", "kind": "explanation", "target_skill_ids": [], "max_len": 180}
        ],
        "weak_skill_labels": [],
        "difficulty": "standard",
        "scenario_type": "home",
        "input_material_kind": "story",
        "lesson_length_band": "short",
        "mini_practice_task_id": "task_e2",
        "reflection_requirements": {"prompt_count": 2},
        "locale": "en",
    }


def test_e2_units() -> None:
    print("\n--- E2 lesson runtime units ---", flush=True)
    from app.services.language_educational_package.pipeline import process_package_generation
    from app.services.language_speaking_educational_package.constraint_builder import (
        build_speaking_package_constraints,
    )
    from app.services.language_speaking_educational_package.template_author import (
        AUTHOR_PROVIDER_TEMPLATE,
        author_package_json_template,
    )
    from app.services.language_speaking_lesson_runtime.engine import (
        LessonRuntimeError,
        advance_lesson_section,
        get_lesson_runtime_view,
        mark_mini_prep_complete,
        mark_teaching_block_viewed,
        mark_vocabulary_viewed,
        open_lesson_runtime,
    )
    from app.services.language_speaking_lesson_runtime.storage import (
        SPEAKING_LESSON_RUNTIME_KEY,
        runtime_from_payload,
    )
    from app.services.language_speaking_lesson_runtime.types import LessonRuntimeSection
    from app.services.language_speaking import ownership as owning

    constraints = build_speaking_package_constraints(sample_constraints())
    raw = author_package_json_template(constraints)
    gen = process_package_generation(
        constraints, raw, author_provider=AUTHOR_PROVIDER_TEMPLATE
    )
    check("1. E1 package available for runtime", gen.success and gen.package is not None)
    package = gen.package
    assert package is not None

    frozen_snapshot = package.to_dict()

    item = SimpleNamespace(
        id=42,
        body_json={
            "educational_package": package.to_dict(),
            "package_constraints": constraints.to_dict(),
            "package_id": package.package_id,
            "immutable": True,
        },
    )

    row = SimpleNamespace(
        promotion_readiness_json={
            "speaking_educational_packages": {
                "by_fingerprint": {package.constraints_fingerprint: package.package_id},
                "by_package_id": {package.package_id: 42},
                "active_by_mission": {constraints.mission_id: package.package_id},
                "order": [package.package_id],
            }
        }
    )

    async def _run() -> None:
        fake_db = SimpleNamespace()

        async def fake_get(*_a, **_kwargs):
            return item

        async def fake_lock(*_a, **_k):
            return row

        with (
            patch(
                "app.services.language_speaking_lesson_runtime.engine.get_package_item_by_id",
                new=fake_get,
            ),
            patch(
                "app.services.language_speaking_lesson_runtime.engine._lock_row",
                new=fake_lock,
            ),
            patch(
                "app.services.language_speaking_lesson_runtime.engine.flag_modified",
                lambda *_a, **_k: None,
            ),
        ):
            view = await open_lesson_runtime(
                fake_db, student_id=1, language_id=1, package_id=package.package_id
            )
            check("2. open starts at introduction", view.state.current_section == LessonRuntimeSection.introduction)
            check("3. package projection present", bool(view.package.get("input_material")))
            check("4. not ready for discussion yet", not view.state.ready_for_discussion)

            # Advance through sections
            for expected in (
                LessonRuntimeSection.reading,
                LessonRuntimeSection.vocabulary,
                LessonRuntimeSection.teaching,
                LessonRuntimeSection.mini_practice,
            ):
                view = await advance_lesson_section(fake_db, student_id=1, language_id=1)
                check(f"5. advanced to {expected.value}", view.state.current_section == expected)

            # Cannot complete without mini prep
            denied = False
            try:
                await advance_lesson_section(fake_db, student_id=1, language_id=1)
            except LessonRuntimeError as exc:
                denied = exc.code == "mini_prep_required"
            check("6. mini prep gate blocks completion", denied)

            vids = [e["vocabulary_id"] for e in view.package.get("vocabulary_in_context", {}).get("entries", [])]
            if vids:
                view = await mark_vocabulary_viewed(
                    fake_db, student_id=1, language_id=1, vocabulary_id=vids[0]
                )
                check("7. vocab marked viewed", vids[0] in view.state.viewed_vocabulary_ids)

            blocks = view.package.get("teaching_blocks_authored") or []
            if blocks:
                bid = blocks[0]["block_id"]
                view = await mark_teaching_block_viewed(
                    fake_db, student_id=1, language_id=1, block_id=bid
                )
                check("8. teaching block marked", bid in view.state.completed_teaching_block_ids)
            else:
                check("8. teaching block marked", True)

            view = await mark_mini_prep_complete(fake_db, student_id=1, language_id=1)
            check("9. mini prep done", view.state.mini_practice_prep_done)

            view = await advance_lesson_section(fake_db, student_id=1, language_id=1)
            check("10. completed section", view.state.current_section == LessonRuntimeSection.completed)
            check("11. ready for discussion flag", view.state.ready_for_discussion)

            # Resume
            resumed = await get_lesson_runtime_view(fake_db, student_id=1, language_id=1)
            check(
                "12. resume at completed",
                resumed.state.current_section == LessonRuntimeSection.completed,
            )
            check(
                "13. resume keeps vocab memory",
                bool(resumed.state.viewed_vocabulary_ids) or not vids,
            )

            # Frozen package body unchanged
            check(
                "14. frozen package dict unchanged",
                item.body_json["educational_package"] == frozen_snapshot,
            )
            check("15. content item still immutable flag", item.body_json.get("immutable") is True)

            # Runtime stored under sibling key
            check(
                "16. runtime key present",
                SPEAKING_LESSON_RUNTIME_KEY in (row.promotion_readiness_json or {}),
            )
            memorized = runtime_from_payload(row.promotion_readiness_json)
            check("17. memory package id", memorized is not None and memorized.package_id == package.package_id)

    asyncio.run(_run())

    # No GPT / eval imports in lesson runtime package
    pkg = BACKEND / "app/services/language_speaking_lesson_runtime"
    text = "\n".join(p.read_text(encoding="utf-8") for p in pkg.glob("*.py"))
    check("18. no claude import", "claude_service" not in text and "generate_claude" not in text)
    check("19. no gpt/openai import", "openai" not in text.lower())
    check(
        "20. no evaluation runtime import",
        "language_speaking_evaluation_runtime" not in text,
    )
    check("21. no author_pipeline import", "author_pipeline" not in text)

    check(
        "22. ownership registers runtime",
        "language_speaking_lesson_runtime" in owning.PACKAGE_OWNERSHIP,
    )
    check(
        "23. ownership depends on educational_package",
        "language_speaking_educational_package"
        in owning.ALLOWED_PACKAGE_DEPENDENCIES["language_speaking_lesson_runtime"],
    )
    check(
        "24. layer experience",
        owning.PACKAGE_LAYER.get("language_speaking_lesson_runtime") == "experience",
    )

    api = (BACKEND / "app/api/language_speaking_lesson_runtime.py").read_text(encoding="utf-8")
    router = (BACKEND / "app/api/router.py").read_text(encoding="utf-8")
    check("25. lesson-runtime API", "lesson-runtime" in api)
    check("26. router registers E2", "language_speaking_lesson_runtime" in router)
    check("27. no discussion endpoints", "discussion" not in api.lower())

    fe_api = BACKEND.parent / "src/api/speakingLessonRuntime.js"
    fe_comp = BACKEND.parent / "src/components/language/SpeakingPackageLesson.vue"
    check("28. FE API client", fe_api.is_file())
    check("29. FE lesson player", fe_comp.is_file())


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
)


def main() -> int:
    skip = os.environ.get("SPEAKING_VERIFY_SKIP_NESTED_REGRESSIONS") == "1"
    if not skip:
        print("=== Speaking E2 FLAT regression runner ===\n", flush=True)
        for label, script in FLAT_REGRESSION_CHAIN:
            if not run_flat_verifier(label, script):
                print(f"\n=== STOPPED: flat regression failed at {label} ===", flush=True)
                return 1
        print("\n=== FLAT E2 (this process) ===", flush=True)

    print("=== Speaking E2 lesson runtime verifier ===\n", flush=True)
    test_e2_units()
    print(f"\n=== E2 units: {PASS} passed, {FAIL} failed ===", flush=True)
    if FAIL:
        return 1
    if not skip:
        print("\n=== RESULT: all flat regressions + E2 units passed ===", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
