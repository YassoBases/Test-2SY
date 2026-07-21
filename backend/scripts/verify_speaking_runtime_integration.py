"""Verify Speaking runtime integration (Start Learning → E1 → E2 → E3).

Usage:
  python -u scripts/verify_speaking_runtime_integration.py
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


def test_integration_units() -> None:
    print("\n--- Runtime integration units ---", flush=True)
    from app.services.language_educational_package.lifecycle import PackageLifecycleStatus
    from app.services.language_educational_package.pipeline import process_package_generation
    from app.services.language_speaking_diagnostic.selector import select_speaking_target
    from app.services.language_speaking_discussion.engine import (
        DiscussionRuntimeError,
        advance_discussion_step,
        open_discussion,
        submit_discussion_response,
    )
    from app.services.language_speaking_educational_package.constraint_builder import (
        build_speaking_package_constraints,
    )
    from app.services.language_speaking_educational_package.template_author import (
        AUTHOR_PROVIDER_TEMPLATE,
        author_package_json_template,
    )
    from app.services.language_speaking_knowledge_model.storage import empty_knowledge_model
    from app.services.language_speaking_lesson_planner.planner import assemble_speaking_lesson_blueprint
    from app.services.language_speaking_lesson_runtime.engine import (
        advance_lesson_section,
        mark_mini_prep_complete,
        open_lesson_runtime,
    )
    from app.services.language_speaking_lesson_runtime.types import LessonRuntimeSection
    from app.services.language_speaking_runtime_api.ensure_learning import (
        ensure_learning_package_for_journey,
        start_learning_runtime,
    )
    from app.services.language_speaking_runtime_api.journey_constraints import (
        build_constraints_payload_from_journey,
    )

    km = empty_knowledge_model(student_id=1, language_id=1)
    rec = select_speaking_target(km, official_cefr="A2", speaking_goal="general_english")
    blueprint = assemble_speaking_lesson_blueprint(rec)
    row = SimpleNamespace(
        official_speaking_cefr=SimpleNamespace(value="A2"),
        learning_stage_speaking=1,
        promotion_readiness_json={},
    )
    constraints = build_constraints_payload_from_journey(row=row, blueprint=blueprint, session=None)
    check("1. journey constraints have mission_id", bool(constraints.get("mission_id")))
    check("2. journey constraints have blueprint_id", constraints.get("blueprint_id") == blueprint.blueprint_id)
    check("3. journey constraints speaking skill", constraints.get("skill") == "speaking")

    built = build_speaking_package_constraints(constraints)
    gen = process_package_generation(
        built,
        author_package_json_template(built),
        author_provider=AUTHOR_PROVIDER_TEMPLATE,
    )
    check("4. template package freezes", gen.success and gen.package is not None)
    package = gen.package
    assert package is not None
    frozen_copy = package.to_dict()

    item = SimpleNamespace(
        id=501,
        body_json={
            "educational_package": package.to_dict(),
            "package_id": package.package_id,
            "immutable": True,
            "package_constraints": built.to_dict(),
        },
    )

    gen_calls = {"n": 0}

    async def fake_create(*_a, **_k):
        gen_calls["n"] += 1
        from app.schemas.language_speaking_educational_package import SpeakingLearningPackageOut
        from app.services.language_speaking_educational_package.projection import (
            project_package_for_student,
        )

        return SpeakingLearningPackageOut(
            success=True,
            cached=False,
            content_item_id=item.id,
            package_id=package.package_id,
            status="frozen",
            constraints_fingerprint=package.constraints_fingerprint,
            content_fingerprint=package.content_fingerprint,
            outcome="success",
            package=project_package_for_student(package),
            audit={},
        )

    async def _run() -> None:
        # ensure_learning flushes the session after indexing; the fake honors that.
        fake_db = SimpleNamespace(flush=AsyncMock())
        prog = SimpleNamespace(
            official_speaking_cefr=SimpleNamespace(value="A2"),
            learning_stage_speaking=1,
            promotion_readiness_json={},
        )

        async def fake_get_journey(*_a, **_k):
            return SimpleNamespace()

        async def fake_ensure_row(*_a, **_k):
            return prog

        with (
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.get_speaking_journey",
                new=fake_get_journey,
            ),
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.ensure_progression_row",
                new=fake_ensure_row,
            ),
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.speaking_bucket_from_payload",
                return_value={},
            ),
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.load_s9_state",
                return_value=SimpleNamespace(
                    blueprint=blueprint, session=None, plan=None, attempt_lineage=None
                ),
            ),
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.create_speaking_learning_package_api",
                new=fake_create,
            ),
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.get_package_item_by_id",
                new=AsyncMock(return_value=None),
            ),
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.flag_modified",
                new=lambda *_a, **_k: None,
            ),
        ):
            first = await ensure_learning_package_for_journey(
                fake_db, student_id=1, language_id=1, author_mode="template"
            )
            check("5. first ensure generates", not first.reused and first.package_id == package.package_id)
            check("6. create called once", gen_calls["n"] == 1)

        from app.services.language_speaking_educational_package.storage_index import (
            elp_index_from_payload,
        )

        idx_after_first = elp_index_from_payload(prog.promotion_readiness_json)
        check(
            "6b. ensure syncs index after generate",
            package.package_id in (idx_after_first.get("order") or []),
            str(idx_after_first),
        )

        async def fake_get_pkg2(*_a, **_k):
            return item

        with (
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.get_speaking_journey",
                new=fake_get_journey,
            ),
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.ensure_progression_row",
                new=fake_ensure_row,
            ),
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.speaking_bucket_from_payload",
                return_value={},
            ),
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.load_s9_state",
                return_value=SimpleNamespace(
                    blueprint=blueprint, session=None, plan=None, attempt_lineage=None
                ),
            ),
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.create_speaking_learning_package_api",
                new=fake_create,
            ),
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.get_package_item_by_id",
                new=fake_get_pkg2,
            ),
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.package_from_item",
                return_value=package,
            ),
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.flag_modified",
                new=lambda *_a, **_k: None,
            ),
        ):
            second = await ensure_learning_package_for_journey(
                fake_db, student_id=1, language_id=1, author_mode="template"
            )
            check("7. second ensure reuses", second.reused and second.package_id == package.package_id)
            check("8. no duplicate generate", gen_calls["n"] == 1)
            idx_after_reuse = elp_index_from_payload(prog.promotion_readiness_json)
            check(
                "8b. no duplicate index order entries",
                (idx_after_reuse.get("order") or []).count(package.package_id) == 1,
            )

        from app.schemas.language_speaking_lesson_runtime import LessonRuntimeOut

        async def fake_start_session(*_a, **_k):
            return {"session_id": "sess1", "blueprint_id": blueprint.blueprint_id}

        async def fake_open_lesson(*_a, **_k):
            async def lock(*_a2, **_k2):
                return prog

            async def get_item(*_a2, **_k2):
                return item

            with (
                patch(
                    "app.services.language_speaking_lesson_runtime.engine._lock_row",
                    new=lock,
                ),
                patch(
                    "app.services.language_speaking_lesson_runtime.engine.get_package_item_by_id",
                    new=get_item,
                ),
                patch(
                    "app.services.language_speaking_lesson_runtime.engine.flag_modified",
                    lambda *_a, **_k: None,
                ),
            ):
                view = await open_lesson_runtime(
                    fake_db, student_id=1, language_id=1, package_id=package.package_id
                )
            return LessonRuntimeOut(**view.to_dict())

        with (
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.get_speaking_journey",
                new=fake_get_journey,
            ),
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.start_speaking_session",
                new=fake_start_session,
            ),
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.ensure_learning_package_for_journey",
                AsyncMock(
                    return_value=SimpleNamespace(
                        reused=True,
                        cached=True,
                        package_id=package.package_id,
                        content_item_id=item.id,
                        status="frozen",
                        constraints_fingerprint=package.constraints_fingerprint,
                        content_fingerprint=package.content_fingerprint,
                        package={"package_id": package.package_id},
                    )
                ),
            ),
            patch(
                "app.services.language_speaking_runtime_api.ensure_learning.open_lesson_runtime_api",
                new=fake_open_lesson,
            ),
        ):
            started = await start_learning_runtime(fake_db, student_id=1, language_id=1)
            check("9. start-learning returns lesson", bool(started.get("lesson")))
            check(
                "10. lesson open section introduction",
                (started.get("lesson") or {}).get("state", {}).get("current_section")
                == LessonRuntimeSection.introduction.value,
            )

        async def lock(*_a, **_k):
            return prog

        async def get_item(*_a, **_k):
            return item

        with (
            patch(
                "app.services.language_speaking_lesson_runtime.engine._lock_row",
                new=lock,
            ),
            patch(
                "app.services.language_speaking_lesson_runtime.engine.get_package_item_by_id",
                new=get_item,
            ),
            patch(
                "app.services.language_speaking_lesson_runtime.engine.flag_modified",
                lambda *_a, **_k: None,
            ),
        ):
            view = await open_lesson_runtime(
                fake_db, student_id=1, language_id=1, package_id=package.package_id
            )
            for _ in range(8):
                if view.state.current_section == LessonRuntimeSection.mini_practice:
                    view = await mark_mini_prep_complete(fake_db, student_id=1, language_id=1)
                if view.state.current_section == LessonRuntimeSection.completed:
                    break
                view = await advance_lesson_section(fake_db, student_id=1, language_id=1)
            check("11. lesson completed", view.state.current_section == LessonRuntimeSection.completed)
            check("12. ready_for_discussion true", view.state.ready_for_discussion)

            saved = dict(prog.promotion_readiness_json or {})
            prog.promotion_readiness_json = {
                k: v for k, v in saved.items() if k != "speaking_lesson_runtime"
            }
            denied = False
            with patch(
                "app.services.language_speaking_discussion.engine._lock_row",
                new=lock,
            ):
                try:
                    await open_discussion(
                        fake_db, student_id=1, language_id=1, package_id=package.package_id
                    )
                except DiscussionRuntimeError as exc:
                    denied = exc.code == "lesson_required"
            check("13. discussion blocked without lesson runtime", denied)
            prog.promotion_readiness_json = saved

            with (
                patch(
                    "app.services.language_speaking_discussion.engine._lock_row",
                    new=lock,
                ),
                patch(
                    "app.services.language_speaking_discussion.engine.get_package_item_by_id",
                    new=get_item,
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
                dview = await open_discussion(
                    fake_db, student_id=1, language_id=1, package_id=package.package_id
                )
                check("14. discussion opens after lesson", not dview.state.completed)
                steps_n = len(package.discussion.steps)
                for i in range(steps_n + 2):
                    if dview.state.completed:
                        break
                    step = package.discussion.steps[min(i, steps_n - 1)]
                    if step.step_id not in dview.state.answered_step_ids:
                        dview = await submit_discussion_response(
                            fake_db,
                            student_id=1,
                            language_id=1,
                            student_response=f"Here is my answer number {i} about the lesson focus.",
                        )
                    dview = await advance_discussion_step(fake_db, student_id=1, language_id=1)
                check("15. discussion completed", dview.state.completed)
                check("16. ready_for_alex true", dview.state.ready_for_alex)

            check(
                "17. frozen package immutable",
                item.body_json["educational_package"] == frozen_copy,
            )

    asyncio.run(_run())

    fe_api = BACKEND.parent / "src/api/speakingLearningPackage.js"
    fe_comp = BACKEND.parent / "src/composables/useSpeakingLearningPackage.js"
    fe_view = BACKEND.parent / "src/views/student/languages/StudentLanguageSpeakingView.vue"
    check("18. FE speakingLearningPackage.js", fe_api.is_file())
    check("19. FE useSpeakingLearningPackage.js", fe_comp.is_file())
    view_text = fe_view.read_text(encoding="utf-8") if fe_view.is_file() else ""
    check("20. view calls startLearning", "startLearning" in view_text)
    check("21. view hydrates lesson", "hydrateLesson" in view_text)
    check("22. view auto discussion on ready", "enterDiscussionFromLesson" in view_text)

    api = (BACKEND / "app/api/language_speaking_runtime_integration.py").read_text(encoding="utf-8")
    router = (BACKEND / "app/api/router.py").read_text(encoding="utf-8")
    check("23. start-learning route", "/start-learning" in api)
    check("24. ensure-package route", "/ensure-package" in api)
    check("25. router registers integration", "language_speaking_runtime_integration" in router)

    from app.services.language_speaking import ownership as owning

    check("26. discussion still experience", owning.PACKAGE_LAYER.get("language_speaking_discussion") == "experience")
    check(
        "27. educational_package still generation",
        owning.PACKAGE_LAYER.get("language_speaking_educational_package") == "generation",
    )
    disc = "\n".join(
        p.read_text(encoding="utf-8")
        for p in (BACKEND / "app/services/language_speaking_discussion").glob("*.py")
    )
    check("28. E3 still no evaluation_runtime", "language_speaking_evaluation_runtime" not in disc)

    # silence unused
    _ = PackageLifecycleStatus


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
    ("E3", "verify_speaking_e3_guided_discussion.py"),
    ("E4", "verify_speaking_e4_discussion_eval.py"),
)


def main() -> int:
    skip = os.environ.get("SPEAKING_VERIFY_SKIP_NESTED_REGRESSIONS") == "1"
    if not skip:
        print("=== Speaking runtime integration FLAT regression runner ===\n", flush=True)
        for label, script in FLAT_REGRESSION_CHAIN:
            if not run_flat_verifier(label, script):
                print(f"\n=== STOPPED: flat regression failed at {label} ===", flush=True)
                return 1
        print("\n=== FLAT integration (this process) ===", flush=True)

    print("=== Speaking runtime integration verifier ===\n", flush=True)
    test_integration_units()
    print(f"\n=== Integration units: {PASS} passed, {FAIL} failed ===", flush=True)
    if FAIL:
        return 1
    if not skip:
        print("\n=== RESULT: all flat regressions + integration units passed ===", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
