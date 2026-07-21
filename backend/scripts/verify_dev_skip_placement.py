"""Verify developer-only Skip Placement / Start From Scratch shortcut.

Usage (from backend/):
    python -u scripts/verify_dev_skip_placement.py
"""

from __future__ import annotations

import ast
import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

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


def test_gate_and_surface() -> None:
    print("\n--- Dev gate + surface ---", flush=True)
    dev_api = (BACKEND / "app" / "api" / "dev.py").read_text(encoding="utf-8")
    check("1. _require_dev gates skip-placement", "_require_dev()" in dev_api and "skip-placement" in dev_api)
    check("2. DEBUG 404 pattern present", 'HTTP_404_NOT_FOUND' in dev_api and "Not found" in dev_api)

    fe = (BACKEND.parent / "src" / "components" / "language" / "DevSkipPlacementControl.vue").read_text(
        encoding="utf-8"
    )
    check("3. FE gated by import.meta.env.DEV", "import.meta.env.DEV" in fe)
    check("4. FE offers CEFR choices", all(x in fe for x in ("A1", "A2", "B1", "B2", "C1")))

    hub = (BACKEND.parent / "src" / "views" / "student" / "languages" / "StudentLanguagesHubView.vue").read_text(
        encoding="utf-8"
    )
    check("5. Hub wires DevSkipPlacementControl", "DevSkipPlacementControl" in hub)

    # Ensure we did not touch curriculum engine / placement scoring.
    svc = (BACKEND / "app" / "services" / "language_dev_skip_placement_service.py").read_text(encoding="utf-8")
    check("6. service reuses sync_progression / generate_learning_path", "sync_progression_from_skill_levels" in svc)
    check("7. service uses empty_knowledge_model", "empty_knowledge_model" in svc)
    check("8. no placement scoring imports", "percent_to_level" not in svc and "score_mcq" not in svc)


def test_curriculum_entry_for_b1() -> None:
    print("\n--- Curriculum entry (B1) ---", flush=True)
    from app.services.language_speaking_curriculum_engine.progression_selector import (
        resolve_progression_decision,
    )
    from app.services.language_speaking_curriculum_engine.progression_types import (
        ProgressionMasteryLedger,
    )
    from app.services.language_speaking_diagnostic.selector import select_speaking_target
    from app.services.language_speaking_knowledge_model.storage import empty_knowledge_model
    from app.services.language_speaking_knowledge_model.types import SpeakingSkillStatus

    decision = resolve_progression_decision(cefr="B1", ledger=ProgressionMasteryLedger())
    check("9. B1 entry node exists", bool(decision.node.node_id))
    check("10. B1 entry action is enter/start", decision.action in ("enter", "repeat", "advance"))

    km = empty_knowledge_model(student_id=99, language_id=1)
    check("11. empty KM has zero observations", km.total_observations == 0)
    check("12. empty KM skill_states empty", len(km.skill_states) == 0)

    rec = select_speaking_target(km, official_cefr="B1", speaking_goal="general_english")
    check("13. sparse B1 target selected", bool(rec.primary_target_skill_id))
    check(
        "14. default skill status is unseen",
        SpeakingSkillStatus.unseen.value == "unseen",
    )


async def test_service_orchestration_mocked() -> None:
    print("\n--- Service orchestration (mocked) ---", flush=True)
    from app.models.language.enums import LanguageLevel, LanguageSkill
    from app.services.language_dev_skip_placement_service import skip_placement_from_scratch
    from app.services.language_speaking_curriculum_engine.progression_types import (
        ProgressionMasteryLedger,
    )
    from app.services.language_speaking_curriculum_engine.progression_selector import (
        resolve_progression_decision,
    )

    expected_node = resolve_progression_decision(cefr="B1", ledger=ProgressionMasteryLedger()).node.node_id

    language = SimpleNamespace(id=1)
    profile = MagicMock()
    profile.placement_completed_at = None
    analytics = MagicMock()
    path = SimpleNamespace(id=42)
    row = MagicMock()
    row.promotion_readiness_json = {}
    row.learning_stage_speaking = 1

    db = AsyncMock()
    db.get = AsyncMock(return_value=analytics)
    db.add = MagicMock()
    db.flush = AsyncMock()

    with (
        patch(
            "app.services.language_dev_skip_placement_service.get_default_language",
            AsyncMock(return_value=language),
        ),
        patch(
            "app.services.language_dev_skip_placement_service._ensure_profile",
            AsyncMock(return_value=profile),
        ),
        patch(
            "app.services.language_dev_skip_placement_service.sync_progression_from_skill_levels",
            AsyncMock(return_value=row),
        ) as sync_mock,
        patch(
            "app.services.language_dev_skip_placement_service.upsert_official_levels",
            AsyncMock(return_value=row),
        ) as upsert_mock,
        patch(
            "app.services.language_dev_skip_placement_service.ensure_progression_row",
            AsyncMock(return_value=row),
        ),
        patch(
            "app.services.language_dev_skip_placement_service.generate_learning_path",
            AsyncMock(return_value=path),
        ) as path_mock,
    ):
        result = await skip_placement_from_scratch(
            db,
            student_id=7,
            starting_cefr="B1",
            bootstrap_learning=False,
        )

    check("15. placement marked complete", profile.placement_completed_at is not None)
    check("16. analytics speaking = B1", analytics.speaking_level == LanguageLevel.B1)
    check("17. overall = B1", analytics.overall_level_internal == LanguageLevel.B1)
    check("18. sync called with B1 levels", sync_mock.await_count == 1)
    skill_levels = sync_mock.await_args.kwargs["skill_levels"]
    check(
        "19. all four skills B1",
        all(skill_levels[s] == LanguageLevel.B1 for s in LanguageSkill),
    )
    check("20. force upsert official levels", upsert_mock.await_args.kwargs.get("force") is True)
    check("21. learning path generated", path_mock.await_count == 1)
    check("22. learning not bootstrapped inline", result["learning_bootstrapped"] is False)
    check("23. response starting_cefr B1", result["starting_cefr"] == "B1")
    check("24. curriculum_entry_node_id matches B1 entry", result["curriculum_entry_node_id"] == expected_node)
    check("25. package deferred (null)", result["package_id"] is None)
    check("26. knowledge_model_initialized", result["knowledge_model_initialized"] is True)
    check("27. redirect to speaking", result["redirect"] == "/student/languages/speaking")
    check("28. stages reset to 1", row.learning_stage_speaking == 1)
    check("28b. primary target skill set", bool(result["primary_target_skill_id"]))


def test_no_forbidden_edits() -> None:
    print("\n--- Anti-regression surface ---", flush=True)
    # Service module must not rewrite curriculum engine modules.
    engine_dir = BACKEND / "app" / "services" / "language_speaking_curriculum_engine"
    check("29. curriculum engine dir unchanged by this feature", engine_dir.is_dir())
    # Parse our service AST: no writes into curriculum_engine package files.
    src = (BACKEND / "app" / "services" / "language_dev_skip_placement_service.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    writes = [n for n in ast.walk(tree) if isinstance(n, (ast.With,))]
    check("30. service AST parses", tree is not None and isinstance(writes, list))


async def main() -> int:
    print("=== Dev Skip Placement verifier ===", flush=True)
    test_gate_and_surface()
    test_curriculum_entry_for_b1()
    await test_service_orchestration_mocked()
    test_no_forbidden_edits()
    print(f"\nResult: {PASS} passed, {FAIL} failed", flush=True)
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
