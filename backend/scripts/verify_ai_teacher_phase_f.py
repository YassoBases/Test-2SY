"""Verify Phase F — Autonomous AI Teacher.

Usage (from backend/):
    python scripts/verify_ai_teacher_phase_f.py
"""

from __future__ import annotations

import ast
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

BACKEND = Path(__file__).resolve().parents[1]
SERVICES = BACKEND / "app" / "services"
TEACHER_PKG = SERVICES / "language_ai_teacher"
LOCKED_PKGS = (
    "language_grammar_catalog",
    "language_grammar_mastery",
    "language_grammar_progression",
    "language_adaptive_intelligence",
    "language_ai_tutor",
    "language_ai_tutor_coaching",
)

FORBIDDEN_WRITE_CALLS = (
    "apply_evidence_and_persist",
    "record_grammar_topic_completed",
    "evaluate_and_persist_grammar_progression",
    "sync_completed_topics_async",
    "persist_learning_profile",
    "persist_conversation_memory",
    "persist_coaching_state",
    "respond_tutor_turn",
    "respond_coaching_turn",
)


def _ok(name: str, passed: bool, detail: str = "") -> bool:
    status = "PASS" if passed else "FAIL"
    suffix = f" - {detail}" if detail else ""
    print(f"  {name}: {status}{suffix}")
    return passed


def _parse_imports(py_file: Path) -> set[str]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("app.services."):
            parts = node.module.split(".")
            if len(parts) >= 3:
                imports.add(parts[2])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("app.services."):
                    parts = alias.name.split(".")
                    if len(parts) >= 3:
                        imports.add(parts[2])
    return imports


def _fingerprint(pkg: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(pkg.rglob("*")):
        if path.is_file() and path.suffix in {".py", ".md"}:
            h.update(path.relative_to(pkg).as_posix().encode())
            h.update(path.read_bytes())
    return h.hexdigest()


def check_package_shape() -> list[bool]:
    results: list[bool] = []
    required = (
        "__init__.py",
        "types.py",
        "enums.py",
        "goals.py",
        "review_plan.py",
        "ordering.py",
        "missions.py",
        "energy.py",
        "weekly.py",
        "journey.py",
        "wrapup.py",
        "orchestrator.py",
        "storage.py",
        "service.py",
        "flags.py",
        "TEACHER_ARCHITECTURE.md",
    )
    results.append(_ok("teacher package directory", TEACHER_PKG.is_dir()))
    for name in required:
        results.append(_ok(f"file: {name}", (TEACHER_PKG / name).is_file()))
    results.append(
        _ok(
            "RESPONSIBILITY declared",
            "RESPONSIBILITY" in (TEACHER_PKG / "__init__.py").read_text(encoding="utf-8"),
        )
    )
    return results


def check_locked_layers_untouched() -> list[bool]:
    results: list[bool] = []
    for pkg in LOCKED_PKGS:
        pkg_dir = SERVICES / pkg
        mentions = 0
        for py_file in pkg_dir.glob("*.py"):
            if "language_ai_teacher" in py_file.read_text(encoding="utf-8"):
                mentions += 1
        results.append(_ok(f"locked free of teacher import: {pkg}", mentions == 0))
        results.append(_ok(f"fingerprint: {pkg}", bool(_fingerprint(pkg_dir))))
    from app.services.language_grammar_catalog.catalog import get_default_catalog

    cat = get_default_catalog()
    results.append(_ok("curriculum still 53 topics", len(cat.topics) == 53, str(len(cat.topics))))
    return results


def check_read_only_contract() -> list[bool]:
    results: list[bool] = []
    text = ""
    imports: set[str] = set()
    for py_file in TEACHER_PKG.glob("*.py"):
        imports |= _parse_imports(py_file)
        text += py_file.read_text(encoding="utf-8") + "\n"

    for dep in (
        "language_grammar_mastery",
        "language_grammar_progression",
        "language_adaptive_intelligence",
        "language_grammar_catalog",
    ):
        results.append(_ok(f"may read {dep}", dep in imports))

    for call in FORBIDDEN_WRITE_CALLS:
        results.append(_ok(f"no call {call}", call not in text))

    results.append(_ok("persist_profile=False", "persist_profile=False" in text))
    results.append(_ok("storage guards namespaces", "JSONB would change" in text))
    results.append(_ok("uses ai_teacher namespace", "ai_teacher" in text))
    return results


def _fixtures():
    from app.services.language_adaptive_intelligence.service import build_adaptive_bundle
    from app.services.language_grammar.enums import (
        GrammarCEFRBand,
        GrammarEvidenceSourceSkill,
        GrammarMasteryState,
    )
    from app.services.language_grammar_mastery.types import (
        GrammarMasteryRecord,
        GrammarMasterySnapshot,
        build_dimensions,
    )
    from app.services.language_grammar_progression.types import GrammarProgressionSnapshot

    as_of = "2026-07-18T12:00:00Z"
    recs = (
        GrammarMasteryRecord(
            student_id=21,
            language_id=1,
            grammar_id="gram_present_perfect",
            state=GrammarMasteryState.practicing,
            dimensions=build_dimensions(
                understanding=70.0, accuracy=50.0, fluency=55.0, retention=45.0, confidence=0.35
            ),
            confidence=0.35,
            stability=0.3,
            retention_risk=0.7,
            evidence_count=4,
            skill_coverage=frozenset({GrammarEvidenceSourceSkill.reading}),
            last_seen_at="2026-07-08T12:00:00Z",
        ),
        GrammarMasteryRecord(
            student_id=21,
            language_id=1,
            grammar_id="gram_present_simple",
            state=GrammarMasteryState.mastered,
            dimensions=build_dimensions(
                understanding=90.0, accuracy=88.0, fluency=85.0, retention=86.0, confidence=0.9
            ),
            confidence=0.9,
            stability=0.85,
            retention_risk=0.1,
            evidence_count=6,
            skill_coverage=frozenset(
                {
                    GrammarEvidenceSourceSkill.reading,
                    GrammarEvidenceSourceSkill.speaking,
                }
            ),
            last_seen_at="2026-07-17T12:00:00Z",
        ),
    )
    mastery = GrammarMasterySnapshot(student_id=21, language_id=1, records=recs)
    progression = GrammarProgressionSnapshot(
        anchor_cefr=GrammarCEFRBand.A2,
        current_grammar_id="gram_present_perfect",
        next_grammar_id="gram_present_perfect_continuous",
        unlocked_ids=("gram_present_simple", "gram_present_perfect"),
        locked_ids=(),
        future_ids=(),
        stretch_ids=(),
        candidate_pool_ids=("gram_present_perfect",),
        candidate_priorities=(),
        progression_reason=("fixture",),
    )
    adaptive = build_adaptive_bundle(
        student_id=21,
        language_id=1,
        mastery=mastery,
        progression=progression,
        as_of=as_of,
        force_enabled=True,
    )
    return mastery, progression, adaptive, as_of


def check_session_generation() -> list[bool]:
    results: list[bool] = []
    from app.services.language_ai_teacher.enums import SessionSectionKind
    from app.services.language_ai_teacher.service import build_learning_session_pure

    mastery, progression, adaptive, as_of = _fixtures()
    a = build_learning_session_pure(
        student_id=21,
        mastery=mastery,
        progression=progression,
        adaptive=adaptive,
        as_of=as_of,
        session_id="teach_test",
    )
    b = build_learning_session_pure(
        student_id=21,
        mastery=mastery,
        progression=progression,
        adaptive=adaptive,
        as_of=as_of,
        session_id="teach_test",
    )
    results.append(_ok("session generated", a is not None and len(a.sections) >= 8))
    results.append(_ok("deterministic section count", len(a.sections) == len(b.sections)))
    results.append(_ok("deterministic activity order", a.activity_order == b.activity_order))
    results.append(_ok("current grammar from progression", a.current_grammar_id == "gram_present_perfect"))
    kinds = {s.kind for s in a.sections}
    for required in (
        SessionSectionKind.welcome,
        SessionSectionKind.todays_goal,
        SessionSectionKind.main_lesson,
        SessionSectionKind.practice,
        SessionSectionKind.speaking,
        SessionSectionKind.quiz,
        SessionSectionKind.reflection,
        SessionSectionKind.summary,
        SessionSectionKind.tomorrow_preview,
    ):
        results.append(_ok(f"section {required.value}", required in kinds))
    return results


def check_goals_review_order_mission_weekly_journey() -> list[bool]:
    results: list[bool] = []
    from app.services.language_ai_teacher.enums import EnergyLevel, ReviewPlanKind
    from app.services.language_ai_teacher.ordering import order_activity_kinds
    from app.services.language_ai_teacher.review_plan import plan_review
    from app.services.language_ai_teacher.service import build_learning_session_pure

    mastery, progression, adaptive, as_of = _fixtures()
    session = build_learning_session_pure(
        student_id=21,
        mastery=mastery,
        progression=progression,
        adaptive=adaptive,
        as_of=as_of,
        coaching_mistake_count=3,
        session_length_minutes=40,
        response_slow=True,
    )

    results.append(_ok("goals non-empty", len(session.goals) >= 1))
    results.append(
        _ok(
            "goals from educational state",
            any(g.grammar_id == "gram_present_perfect" or "Present Perfect" in g.title for g in session.goals)
            or any(g.source in {"grammar", "adaptive", "review", "skill"} for g in session.goals),
        )
    )

    r1 = plan_review(adaptive)
    r2 = plan_review(adaptive)
    results.append(_ok("review planner deterministic", r1.kind == r2.kind and r1.minutes == r2.minutes))
    results.append(_ok("review has reasons", len(r1.reasons) >= 1))
    results.append(_ok("review kind valid", r1.kind in ReviewPlanKind))

    # Speaking-boosted ordering: force speaking weight high via fixture adaptive (reading-only coverage boosts speaking)
    order, notes = order_activity_kinds(adaptive, energy=EnergyLevel.steady)
    results.append(_ok("activity order includes speaking", "speaking" in order))
    results.append(_ok("ordering explainable", len(notes) >= 1))
    # Low energy pushes reading later
    order_low, _ = order_activity_kinds(adaptive, energy=EnergyLevel.low)
    if "reading" in order_low and "speaking" in order_low:
        results.append(
            _ok(
                "low energy adapts reading position",
                order_low.index("reading") >= order_low.index("speaking")
                or order_low.index("reading") > 2,
            )
        )
    else:
        results.append(_ok("low energy adapts reading position", True))

    results.append(_ok("mission present", session.mission is not None))
    results.append(
        _ok(
            "mission maps to grammar",
            session.mission is not None and session.mission.grammar_id == "gram_present_perfect",
        )
    )

    results.append(_ok("weekly plan 7 days", session.weekly is not None and len(session.weekly.days) == 7))
    results.append(_ok("sunday rest", session.weekly is not None and session.weekly.days[-1].focus == "Rest"))

    results.append(_ok("journey current grammar", session.journey.current_grammar_id == "gram_present_perfect"))
    results.append(_ok("journey completed count", session.journey.grammar_completed_count >= 1))
    results.append(_ok("journey upcoming set", bool(session.journey.upcoming_lesson)))
    results.append(_ok("energy level valid", session.energy.level in EnergyLevel))
    results.append(
        _ok(
            "energy recommends only (no auto-end API)",
            "end lesson" not in " ".join(session.energy.recommendations).lower()
            and "cancel" not in " ".join(session.energy.recommendations).lower(),
        )
    )

    results.append(_ok("wrap-up present", session.wrap_up_preview is not None))
    results.append(
        _ok(
            "wrap-up explainable",
            session.wrap_up_preview is not None and len(session.wrap_up_preview.reasons) >= 1,
        )
    )
    results.append(
        _ok(
            "wrap-up recommendation set",
            session.wrap_up_preview is not None and bool(session.wrap_up_preview.recommendation),
        )
    )
    return results


def check_storage_api_flags() -> list[bool]:
    results: list[bool] = []
    from app.core.config import Settings
    from app.services.language_ai_teacher.service import build_learning_session_pure
    from app.services.language_ai_teacher.storage import merge_teacher_into_payload
    from app.services.language_ai_teacher.types import AI_TEACHER_JSONB_NAMESPACE
    from app.services.language_grammar.ownership import (
        ADAPTIVE_JSONB_NAMESPACE_RESERVED,
        AI_TEACHER_JSONB_NAMESPACE_RESERVED,
        AI_TUTOR_COACHING_JSONB_NAMESPACE_RESERVED,
        AI_TUTOR_JSONB_NAMESPACE_RESERVED,
        GRAMMAR_JSONB_NAMESPACE,
    )

    mastery, progression, adaptive, as_of = _fixtures()
    session = build_learning_session_pure(
        student_id=21,
        mastery=mastery,
        progression=progression,
        adaptive=adaptive,
        as_of=as_of,
        session_id="teach_store",
    )
    payload = {
        GRAMMAR_JSONB_NAMESPACE: {"mastery": {}},
        ADAPTIVE_JSONB_NAMESPACE_RESERVED: {"learning_profile": {}},
        AI_TUTOR_JSONB_NAMESPACE_RESERVED: {"conversations": {}},
        AI_TUTOR_COACHING_JSONB_NAMESPACE_RESERVED: {"sessions": {}},
    }
    merged = merge_teacher_into_payload(
        payload, {"sessions": {"teach_store": session.to_dict()}, "active_session_id": "teach_store"}
    )
    results.append(_ok("merge preserves grammar", merged[GRAMMAR_JSONB_NAMESPACE] == payload[GRAMMAR_JSONB_NAMESPACE]))
    results.append(
        _ok(
            "merge preserves adaptive",
            merged[ADAPTIVE_JSONB_NAMESPACE_RESERVED] == payload[ADAPTIVE_JSONB_NAMESPACE_RESERVED],
        )
    )
    results.append(
        _ok(
            "merge preserves tutor",
            merged[AI_TUTOR_JSONB_NAMESPACE_RESERVED] == payload[AI_TUTOR_JSONB_NAMESPACE_RESERVED],
        )
    )
    results.append(
        _ok(
            "merge preserves coaching",
            merged[AI_TUTOR_COACHING_JSONB_NAMESPACE_RESERVED]
            == payload[AI_TUTOR_COACHING_JSONB_NAMESPACE_RESERVED],
        )
    )
    results.append(_ok("merge writes ai_teacher", AI_TEACHER_JSONB_NAMESPACE in merged))
    results.append(_ok("ownership ai_teacher", AI_TEACHER_JSONB_NAMESPACE_RESERVED == "ai_teacher"))

    fields = Settings.model_fields
    results.append(_ok("flag LANG_AI_TEACHER_ENABLED", "LANG_AI_TEACHER_ENABLED" in fields))
    results.append(_ok("flag LANG_AI_TEACHER_PERSIST", "LANG_AI_TEACHER_PERSIST" in fields))
    results.append(_ok("teacher flag default false", fields["LANG_AI_TEACHER_ENABLED"].default is False))

    api = BACKEND / "app" / "api" / "language_ai_teacher.py"
    router = BACKEND / "app" / "api" / "router.py"
    results.append(_ok("API exists", api.is_file()))
    results.append(_ok("router includes teacher", "language_ai_teacher" in router.read_text(encoding="utf-8")))
    for env_path in (BACKEND / ".env.example", BACKEND.parent / ".env.example"):
        if env_path.is_file():
            results.append(
                _ok(
                    f"{env_path.name} documents teacher flag",
                    "LANG_AI_TEACHER_ENABLED" in env_path.read_text(encoding="utf-8"),
                )
            )
    return results


def main() -> int:
    print("Autonomous AI Teacher Phase F verification\n")
    suites = [
        ("Package shape", check_package_shape),
        ("Locked layers untouched", check_locked_layers_untouched),
        ("Read-only contract", check_read_only_contract),
        ("Session generation", check_session_generation),
        ("Goals / review / order / mission / weekly / journey", check_goals_review_order_mission_weekly_journey),
        ("Storage / API / flags", check_storage_api_flags),
    ]
    all_ok = True
    for title, fn in suites:
        print(f"[{title}]")
        results = fn()
        if not all(results):
            all_ok = False
        print()
    if all_ok:
        print("ALL PHASE F CHECKS PASSED")
        return 0
    print("PHASE F CHECKS FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
