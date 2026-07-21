"""Verify Speaking E1 Learning Package generation pipeline.

Usage:
  python -u scripts/verify_speaking_e1_learning_package.py
  $env:SPEAKING_VERIFY_SKIP_NESTED_REGRESSIONS='1'  # units only
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
        "mission_id": "mission_demo_1",
        "mission_kind": "guided_practice",
        "execution_mode": "controlled_response",
        "evidence_intent": "formative",
        "blueprint_id": "bp_demo",
        "blueprint_hash": "hash_demo_abc",
        "learning_focus": "ordering food politely",
        "objectives": ["Ask for a menu item", "Use polite phrases"],
        "vocabulary_ids": ["vocab_menu", "vocab_please"],
        "vocabulary_surface_forms": ["menu", "please"],
        "grammar_topic_ids": ["polite_requests"],
        "teaching_block_specs": [
            {
                "block_id": "tb_1",
                "kind": "explanation",
                "target_skill_ids": ["polite_requests"],
                "max_len": 200,
            }
        ],
        "weak_skill_labels": ["politeness"],
        "difficulty": "standard",
        "scenario_type": "restaurant",
        "input_material_kind": "story",
        "lesson_length_band": "standard",
        "mini_practice_task_id": "task_speak_1",
        "reflection_requirements": {"prompt_count": 2},
        "locale": "en",
    }


def test_pipeline_units() -> None:
    print("\n--- E1 pipeline units ---", flush=True)
    from app.services.language_educational_package.fingerprint import (
        compute_constraints_fingerprint,
        compute_content_fingerprint,
    )
    from app.services.language_educational_package.lifecycle import PackageLifecycleStatus
    from app.services.language_educational_package.pipeline import (
        GenerationOutcome,
        process_package_generation,
    )
    from app.services.language_educational_package.validation import validate_package_draft
    from app.services.language_speaking_educational_package.constraint_builder import (
        build_speaking_package_constraints,
    )
    from app.services.language_speaking_educational_package.template_author import (
        AUTHOR_PROVIDER_TEMPLATE,
        author_package_json_template,
    )
    from app.services.language_speaking_educational_package.storage_index import (
        elp_index_from_payload,
        record_package_in_index,
    )
    from app.services.language_speaking import ownership as owning

    constraints = build_speaking_package_constraints(sample_constraints())
    check("1. constraints skill speaking", constraints.skill == "speaking")
    check("2. constraints cefr A2", constraints.official_cefr == "A2")
    fp1 = compute_constraints_fingerprint(constraints)
    fp2 = compute_constraints_fingerprint(constraints)
    check("3. constraints fingerprint stable", fp1 == fp2 and fp1.startswith("elp_c_"))

    raw = author_package_json_template(constraints)
    result = process_package_generation(
        constraints,
        raw,
        author_provider=AUTHOR_PROVIDER_TEMPLATE,
        attempt_repair=True,
    )
    check("4. generation success", result.success)
    check("5. outcome success|soft", result.outcome in {GenerationOutcome.success, GenerationOutcome.soft_failure})
    assert result.package is not None
    check("6. status frozen", result.package.status == PackageLifecycleStatus.frozen)
    check("7. package_id set", bool(result.package.package_id))
    check("8. content fingerprint set", result.package.content_fingerprint.startswith("elp_p_"))
    check("9. vocab coverage", len(result.package.vocabulary_in_context.entries) >= 2)
    check("10. discussion steps present", len(result.package.discussion.steps) >= 4)
    check("11. reflection present", len(result.package.reflection.prompts) >= 2)
    check(
        "12. mini practice task id",
        result.package.mini_practice.task_id == "task_speak_1",
    )
    check(
        "13. cefr echo",
        result.package.input_material.cefr_check_echo == "A2",
    )
    check(
        "13b. story material kind",
        result.package.input_material.kind.value == "story",
    )
    check(
        "13c. story spine substantive",
        result.package.story_spine.is_substantive(),
    )
    check("14. immutable freeze", result.package.status.value == "frozen")

    # Repair path: incomplete raw JSON missing discussion → repair rebuilds
    incomplete = """
    {
      "input_material": {"kind": "story", "title": "Hi", "body_blocks": [{"kind": "paragraph", "text": "x", "block_ref": "b0"}], "cefr_check_echo": "A2"},
      "vocabulary_in_context": {"entries": [], "highlight_map": []},
      "discussion": {"flow_id": "", "opening_move": "", "steps": [], "closing_move": ""},
      "reflection": {"prompts": [], "self_check_cues": []}
    }
    """
    repaired = process_package_generation(
        constraints,
        incomplete,
        author_provider=AUTHOR_PROVIDER_TEMPLATE,
        attempt_repair=True,
    )
    check("15. repair path succeeds", repaired.success)
    check("16. repair recorded", bool(repaired.repair and repaired.repair.repaired))

    # Hard fail: invalid JSON
    bad = process_package_generation(
        constraints,
        "not-json",
        author_provider=AUTHOR_PROVIDER_TEMPLATE,
        attempt_repair=True,
    )
    check("17. invalid JSON hard failure", not bad.success and bad.outcome == GenerationOutcome.hard_failure)

    # Resume index
    payload = record_package_in_index(
        {},
        package_id=result.package.package_id,
        constraints_fingerprint=result.package.constraints_fingerprint,
        mission_id=constraints.mission_id,
        content_item_id=99,
    )
    index = elp_index_from_payload(payload)
    check(
        "18. resume index by mission",
        index["active_by_mission"].get(constraints.mission_id) == result.package.package_id,
    )
    check(
        "19. resume index by fingerprint",
        index["by_fingerprint"].get(result.package.constraints_fingerprint)
        == result.package.package_id,
    )

    # Re-validate frozen package
    v = validate_package_draft(result.package, constraints)
    check("20. frozen package validates", v.passed, str([i.message for i in v.issues]))

    # Round-trip serialize
    from app.services.language_educational_package.types import EducationalPackage

    again = EducationalPackage.from_dict(result.package.to_dict())
    check("21. serialize round-trip id", again.package_id == result.package.package_id)
    check(
        "22. content fingerprint stable after round-trip",
        compute_content_fingerprint(again) == result.package.content_fingerprint
        or again.content_fingerprint == result.package.content_fingerprint,
    )

    check(
        "23. ownership registers ELP package",
        "language_speaking_educational_package" in owning.PACKAGE_OWNERSHIP,
    )
    check(
        "24. ownership layer generation",
        owning.PACKAGE_LAYER.get("language_speaking_educational_package") == "generation",
    )

    api = BACKEND / "app/api/language_speaking_educational_package.py"
    router = (BACKEND / "app/api/router.py").read_text(encoding="utf-8")
    check("25. API module exists", api.is_file())
    check("26. router registers E1", "language_speaking_educational_package" in router)
    check("27. create route prefix", "learning-packages" in api.read_text(encoding="utf-8"))

    # Shared package present
    check(
        "28. shared educational package exists",
        (BACKEND / "app/services/language_educational_package/pipeline.py").is_file(),
    )

    # Generic material kinds
    from app.services.language_educational_package.material_kinds import InputMaterialKind

    check("29. story kind", InputMaterialKind.story.value == "story")
    check("30. menu kind", InputMaterialKind.restaurant_menu.value == "restaurant_menu")


def test_cache_hit_elp_index_consistency() -> None:
    """Cache must not change runtime semantics: index syncs on generate and cache hit."""
    print("\n--- E1 cache / ELP index consistency ---", flush=True)
    from app.services.language_educational_package.pipeline import process_package_generation
    from app.services.language_speaking_educational_package.author_pipeline import (
        generate_speaking_learning_package,
    )
    from app.services.language_speaking_educational_package.constraint_builder import (
        build_speaking_package_constraints,
    )
    from app.services.language_speaking_educational_package.storage_index import (
        SPEAKING_ELP_INDEX_KEY,
        elp_index_from_payload,
    )
    from app.services.language_speaking_educational_package.template_author import (
        AUTHOR_PROVIDER_TEMPLATE,
        author_package_json_template,
    )
    from app.services.language_speaking_lesson_runtime.engine import (
        LessonRuntimeError,
        open_lesson_runtime,
    )

    constraints = build_speaking_package_constraints(sample_constraints())
    # Sanity: template path freezes (also seeds auditor of pipeline health).
    seed = process_package_generation(
        constraints,
        author_package_json_template(constraints),
        author_provider=AUTHOR_PROVIDER_TEMPLATE,
    )
    check("31. seed template freezes", seed.success and seed.package is not None)

    item = SimpleNamespace(id=777, body_json={})
    prog = SimpleNamespace(promotion_readiness_json={})
    persist_calls = {"n": 0}

    async def fake_persist(_db, *, student_id, language_id, package, constraints, audit):
        persist_calls["n"] += 1
        item.body_json = {
            "educational_package": package.to_dict(),
            "package_constraints": constraints.to_dict(),
            "package_id": package.package_id,
            "constraints_fingerprint": package.constraints_fingerprint,
            "content_fingerprint": package.content_fingerprint,
            "immutable": True,
            "status": "frozen",
            "audit": audit or {"author_provider": AUTHOR_PROVIDER_TEMPLATE},
        }
        return item

    async def fake_find_miss(*_a, **_k):
        return None

    async def fake_find_hit(*_a, **_k):
        return item

    async def _run() -> None:
        fake_db = SimpleNamespace()

        with (
            patch(
                "app.services.language_speaking_educational_package.author_pipeline.find_cached_package_item",
                new=fake_find_miss,
            ),
            patch(
                "app.services.language_speaking_educational_package.author_pipeline.persist_frozen_package",
                new=fake_persist,
            ),
            patch(
                "app.services.language_speaking_educational_package.author_pipeline._lock_progression_row",
                new=AsyncMock(return_value=prog),
            ),
        ):
            first = await generate_speaking_learning_package(
                fake_db,
                student_id=1,
                language_id=1,
                constraints_payload=sample_constraints(),
                author_mode="template",
                use_cache=True,
            )

        check("32. generate success", first.success and not first.cached and first.package is not None)
        check("33. generate persisted once", persist_calls["n"] == 1)
        package_id = first.package.package_id  # type: ignore[union-attr]
        idx1 = elp_index_from_payload(prog.promotion_readiness_json)
        check("34. index populated after generate", package_id in (idx1.get("order") or []))
        check(
            "35. active_by_mission after generate",
            idx1.get("active_by_mission", {}).get(constraints.mission_id) == package_id,
        )

        # Simulate prior content-store cache without index (the ownership bug).
        prog.promotion_readiness_json = {}
        check(
            "36. index cleared for cache-hit scenario",
            not (elp_index_from_payload(prog.promotion_readiness_json).get("order") or []),
        )

        with (
            patch(
                "app.services.language_speaking_educational_package.author_pipeline.find_cached_package_item",
                new=fake_find_hit,
            ),
            patch(
                "app.services.language_speaking_educational_package.author_pipeline.persist_frozen_package",
                new=fake_persist,
            ),
            patch(
                "app.services.language_speaking_educational_package.author_pipeline._lock_progression_row",
                new=AsyncMock(return_value=prog),
            ),
        ):
            second = await generate_speaking_learning_package(
                fake_db,
                student_id=1,
                language_id=1,
                constraints_payload=sample_constraints(),
                author_mode="template",
                use_cache=True,
            )

        check("37. cache hit success", second.success and second.cached)
        check("38. no duplicate persist on cache hit", persist_calls["n"] == 1)
        check("39. cache returns same package_id", second.package and second.package.package_id == package_id)
        idx2 = elp_index_from_payload(prog.promotion_readiness_json)
        check(
            "40. index populated after cache hit",
            package_id in (idx2.get("order") or []),
            str(idx2),
        )
        check(
            "41. no duplicate order entries",
            (idx2.get("order") or []).count(package_id) == 1,
        )
        check(
            "42. by_package_id maps content item",
            idx2.get("by_package_id", {}).get(package_id) == item.id,
        )

        with (
            patch(
                "app.services.language_speaking_educational_package.author_pipeline.find_cached_package_item",
                new=fake_find_hit,
            ),
            patch(
                "app.services.language_speaking_educational_package.author_pipeline.persist_frozen_package",
                new=fake_persist,
            ),
            patch(
                "app.services.language_speaking_educational_package.author_pipeline._lock_progression_row",
                new=AsyncMock(return_value=prog),
            ),
        ):
            third = await generate_speaking_learning_package(
                fake_db,
                student_id=1,
                language_id=1,
                constraints_payload=sample_constraints(),
                author_mode="template",
                use_cache=True,
            )
        check("43. second cache hit still cached", third.cached)
        check("44. still one persist", persist_calls["n"] == 1)
        idx3 = elp_index_from_payload(prog.promotion_readiness_json)
        check(
            "45. still no duplicate order entries",
            (idx3.get("order") or []).count(package_id) == 1,
        )
        check(
            "46. index key under promotion_readiness_json",
            SPEAKING_ELP_INDEX_KEY in (prog.promotion_readiness_json or {}),
        )

        async def fake_get_item(*_a, **_k):
            return item

        async def fake_lock(*_a, **_k):
            return prog

        with (
            patch(
                "app.services.language_speaking_lesson_runtime.engine.get_package_item_by_id",
                new=fake_get_item,
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
            opened = await open_lesson_runtime(
                fake_db, student_id=1, language_id=1, package_id=None
            )
            check(
                "47. open latest without package_id succeeds",
                opened.state.package_id == package_id,
            )
            resumed = await open_lesson_runtime(
                fake_db, student_id=1, language_id=1, package_id=None
            )
            check(
                "48. resume without package_id succeeds",
                resumed.state.package_id == package_id,
            )

        prog.promotion_readiness_json = {}
        failed = False
        with (
            patch(
                "app.services.language_speaking_lesson_runtime.engine.get_package_item_by_id",
                new=fake_get_item,
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
            try:
                await open_lesson_runtime(
                    fake_db, student_id=1, language_id=1, package_id=None
                )
            except LessonRuntimeError as exc:
                failed = exc.code == "no_package"
        check("49. empty index still fails open-latest (no workaround)", failed)

    asyncio.run(_run())


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
    status = "OK" if ok else "FAIL"
    print(f"  {status}  {label} (exit={proc.returncode})", flush=True)
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
)


def main() -> int:
    skip = os.environ.get("SPEAKING_VERIFY_SKIP_NESTED_REGRESSIONS") == "1"
    if not skip:
        print("=== Speaking E1 FLAT regression runner ===\n", flush=True)
        for label, script in FLAT_REGRESSION_CHAIN:
            if not run_flat_verifier(label, script):
                print(
                    f"\n=== STOPPED: flat regression failed at {label} ({script}) ===",
                    flush=True,
                )
                return 1
        print("\n=== FLAT E1 (this process) ===", flush=True)

    print("=== Speaking E1 learning package verifier ===\n", flush=True)
    test_pipeline_units()
    test_cache_hit_elp_index_consistency()
    print(f"\n=== E1 units: {PASS} passed, {FAIL} failed ===", flush=True)
    if FAIL:
        return 1
    if not skip:
        print("\n=== RESULT: all flat regressions + E1 units passed ===", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
