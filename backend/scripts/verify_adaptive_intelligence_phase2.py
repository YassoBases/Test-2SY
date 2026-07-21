"""Verify Phase 2 — Adaptive Learning Intelligence.

Usage (from backend/):
    python scripts/verify_adaptive_intelligence_phase2.py
"""

from __future__ import annotations

import ast
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

BACKEND = Path(__file__).resolve().parents[1]
SERVICES = BACKEND / "app" / "services"
ADAPTIVE_PKG = SERVICES / "language_adaptive_intelligence"
CURRICULUM = BACKEND / "curriculum" / "english" / "grammar"
LOCKED_PACKAGES = (
    "language_grammar_catalog",
    "language_grammar_target_resolver",
    "language_grammar_skill_context",
    "language_grammar_mastery",
    "language_grammar_progression",
    "language_grammar_evidence",
    "language_grammar_integrity",
    "language_grammar_lesson_planner",
    "language_grammar_lesson_runtime",
)
FORBIDDEN_WRITE_CALLS = (
    "apply_evidence_and_persist",
    "record_grammar_topic_completed",
    "evaluate_and_persist_grammar_progression",
    "sync_completed_topics_async",
    "complete_attested_activity",
    "append_evidence_ledger",
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


def _curriculum_fingerprint() -> str:
    h = hashlib.sha256()
    for path in sorted(CURRICULUM.rglob("*.yaml")):
        h.update(path.name.encode())
        h.update(path.read_bytes())
    return h.hexdigest()


def _make_record(
    *,
    grammar_id: str,
    understanding: float,
    accuracy: float,
    fluency: float,
    retention: float,
    confidence: float,
    stability: float,
    retention_risk: float,
    evidence_count: int,
    last_seen_at: str,
    skills: frozenset | None = None,
    state=None,
):
    from app.services.language_grammar.enums import (
        GrammarEvidenceSourceSkill,
        GrammarMasteryState,
    )
    from app.services.language_grammar_mastery.types import GrammarMasteryRecord, build_dimensions

    return GrammarMasteryRecord(
        student_id=7,
        language_id=1,
        grammar_id=grammar_id,
        state=state or GrammarMasteryState.practicing,
        dimensions=build_dimensions(
            understanding=understanding,
            accuracy=accuracy,
            fluency=fluency,
            retention=retention,
            confidence=confidence,
        ),
        confidence=confidence,
        stability=stability,
        retention_risk=retention_risk,
        evidence_count=evidence_count,
        distinct_context_count=max(1, min(3, evidence_count)),
        skill_coverage=skills
        or frozenset({GrammarEvidenceSourceSkill.reading}),
        last_seen_at=last_seen_at,
        last_updated_at=last_seen_at,
    )


def _fixture_mastery():
    from app.services.language_grammar.enums import (
        GrammarEvidenceSourceSkill,
        GrammarMasteryState,
    )
    from app.services.language_grammar_mastery.types import GrammarMasterySnapshot

    as_of_anchor = "2026-07-18T12:00:00Z"
    records = (
        _make_record(
            grammar_id="gram_present_perfect",
            understanding=82.0,
            accuracy=48.0,
            fluency=55.0,
            retention=50.0,
            confidence=0.35,
            stability=0.25,
            retention_risk=0.7,
            evidence_count=5,
            last_seen_at="2026-07-09T12:00:00Z",  # 9 days idle
            skills=frozenset({GrammarEvidenceSourceSkill.reading}),
            state=GrammarMasteryState.practicing,
        ),
        _make_record(
            grammar_id="gram_present_simple",
            understanding=90.0,
            accuracy=88.0,
            fluency=85.0,
            retention=86.0,
            confidence=0.9,
            stability=0.85,
            retention_risk=0.15,
            evidence_count=6,
            last_seen_at="2026-07-17T12:00:00Z",
            skills=frozenset(
                {
                    GrammarEvidenceSourceSkill.reading,
                    GrammarEvidenceSourceSkill.speaking,
                    GrammarEvidenceSourceSkill.writing,
                }
            ),
            state=GrammarMasteryState.mastered,
        ),
        _make_record(
            grammar_id="gram_passive_voice",
            understanding=40.0,
            accuracy=42.0,
            fluency=38.0,
            retention=35.0,
            confidence=0.25,
            stability=0.3,
            retention_risk=0.5,
            evidence_count=3,
            last_seen_at="2026-07-10T12:00:00Z",
            skills=frozenset({GrammarEvidenceSourceSkill.writing}),
            state=GrammarMasteryState.learning,
        ),
    )
    return GrammarMasterySnapshot(student_id=7, language_id=1, records=records), as_of_anchor


def _fixture_progression():
    from app.services.language_grammar.enums import GrammarCEFRBand
    from app.services.language_grammar_progression.types import GrammarProgressionSnapshot

    return GrammarProgressionSnapshot(
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


def check_package_shape() -> list[bool]:
    results: list[bool] = []
    required = (
        "__init__.py",
        "types.py",
        "enums.py",
        "confidence.py",
        "signals.py",
        "difficulty.py",
        "recommendations.py",
        "profile.py",
        "teacher.py",
        "parent.py",
        "storage.py",
        "service.py",
        "flags.py",
        "ADAPTIVE_ARCHITECTURE.md",
    )
    results.append(_ok("adaptive package directory", ADAPTIVE_PKG.is_dir()))
    for name in required:
        results.append(_ok(f"file: {name}", (ADAPTIVE_PKG / name).is_file()))
    init_text = (ADAPTIVE_PKG / "__init__.py").read_text(encoding="utf-8")
    results.append(_ok("RESPONSIBILITY declared", "RESPONSIBILITY" in init_text))
    return results


def check_read_only_isolation() -> list[bool]:
    results: list[bool] = []
    adaptive_imports: set[str] = set()
    adaptive_text = ""
    for py_file in ADAPTIVE_PKG.glob("*.py"):
        adaptive_imports |= _parse_imports(py_file)
        adaptive_text += py_file.read_text(encoding="utf-8") + "\n"

    # May read mastery/progression/review/catalog; must not import write owners wrongly
    for dep in (
        "language_grammar_mastery",
        "language_grammar_progression",
        "language_grammar_review",
        "language_grammar_catalog",
    ):
        results.append(_ok(f"may read {dep}", dep in adaptive_imports))

    for forbidden in (
        "language_grammar_pipeline",
        "language_grammar_integrity",
        "language_grammar_lesson_planner",
        "language_grammar_lesson_runtime",
        "language_grammar_target_resolver",
        "language_grammar_skill_context",
        "language_grammar_module",
    ):
        results.append(_ok(f"does not import {forbidden}", forbidden not in adaptive_imports))

    for call in FORBIDDEN_WRITE_CALLS:
        results.append(_ok(f"no call {call}", call not in adaptive_text))

    results.append(
        _ok(
            "storage guards grammar namespace",
            "grammar JSONB would change" in (ADAPTIVE_PKG / "storage.py").read_text(encoding="utf-8"),
        )
    )
    results.append(
        _ok(
            "uses adaptive JSONB namespace",
            "adaptive_intelligence" in (ADAPTIVE_PKG / "types.py").read_text(encoding="utf-8"),
        )
    )
    return results


def check_locked_baselines_untouched() -> list[bool]:
    """Adaptive must not live inside locked package trees (source scan)."""
    results: list[bool] = []
    for pkg in LOCKED_PACKAGES:
        pkg_dir = SERVICES / pkg
        mentions = 0
        for py_file in pkg_dir.glob("*.py"):
            text = py_file.read_text(encoding="utf-8")
            if "language_adaptive_intelligence" in text:
                mentions += 1
        results.append(_ok(f"locked package unchanged by adaptive import: {pkg}", mentions == 0))
    # Curriculum YAML fingerprint still loads 53 topics
    from app.services.language_grammar_catalog.catalog import get_default_catalog

    cat = get_default_catalog()
    results.append(_ok("curriculum still 53 topics", len(cat.topics) == 53, str(len(cat.topics))))
    results.append(_ok("curriculum fingerprint non-empty", bool(_curriculum_fingerprint())))
    return results


def check_deterministic_recommendations() -> list[bool]:
    results: list[bool] = []
    from app.services.language_adaptive_intelligence.service import build_adaptive_bundle

    mastery, as_of = _fixture_mastery()
    progression = _fixture_progression()
    a = build_adaptive_bundle(
        student_id=7,
        language_id=1,
        mastery=mastery,
        progression=progression,
        as_of=as_of,
        force_enabled=True,
    )
    b = build_adaptive_bundle(
        student_id=7,
        language_id=1,
        mastery=mastery,
        progression=progression,
        as_of=as_of,
        force_enabled=True,
    )
    results.append(_ok("bundle enabled", a.enabled))
    results.append(_ok("deterministic review count", len(a.review_recommendations) == len(b.review_recommendations)))
    results.append(
        _ok(
            "deterministic review ids",
            [r.grammar_id for r in a.review_recommendations]
            == [r.grammar_id for r in b.review_recommendations],
        )
    )
    results.append(
        _ok(
            "deterministic difficulty",
            a.difficulty is not None
            and b.difficulty is not None
            and a.difficulty.difficulty_level == b.difficulty.difficulty_level,
        )
    )
    results.append(
        _ok(
            "deterministic activity mix",
            a.activity_mix.as_dict() == b.activity_mix.as_dict(),
        )
    )
    results.append(
        _ok(
            "deterministic signals",
            [(s.kind.value, s.grammar_id) for s in a.signals]
            == [(s.kind.value, s.grammar_id) for s in b.signals],
        )
    )
    results.append(
        _ok(
            "deterministic remediations",
            [(m.kind.value, m.grammar_id) for m in a.remediations]
            == [(m.kind.value, m.grammar_id) for m in b.remediations],
        )
    )
    return results


def check_explainability() -> list[bool]:
    results: list[bool] = []
    from app.services.language_adaptive_intelligence.service import build_adaptive_bundle

    mastery, as_of = _fixture_mastery()
    progression = _fixture_progression()
    bundle = build_adaptive_bundle(
        student_id=7,
        language_id=1,
        mastery=mastery,
        progression=progression,
        as_of=as_of,
        force_enabled=True,
    )
    results.append(_ok("has review recommendations", len(bundle.review_recommendations) >= 1))
    for rec in bundle.review_recommendations:
        results.append(_ok(f"review reasons: {rec.grammar_id}", len(rec.reasons) >= 1))
        results.append(
            _ok(
                f"review explanation bullets: {rec.grammar_id}",
                "because:" in rec.explanation and "•" in rec.explanation,
            )
        )
    results.append(_ok("difficulty has reasons", bundle.difficulty is not None and len(bundle.difficulty.reasons) >= 1))
    results.append(_ok("activity mix has reasons", len(bundle.activity_mix.reasons) >= 1))
    for rem in bundle.remediations:
        results.append(_ok(f"remediation explainable: {rem.kind.value}", "because:" in rem.explanation))
    results.append(_ok("teacher explanations", len(bundle.teacher.explanations) >= 1))
    results.append(_ok("parent explanations", len(bundle.parent.explanations) >= 1))
    # Present Perfect example surface
    pp = next((r for r in bundle.review_recommendations if r.grammar_id == "gram_present_perfect"), None)
    results.append(_ok("present perfect review present", pp is not None))
    if pp is not None:
        joined = " ".join(r.message.lower() for r in pp.reasons)
        results.append(_ok("mentions confidence or mistakes or days", any(
            token in joined for token in ("confidence", "accuracy", "days", "retention")
        )))
    return results


def check_components() -> list[bool]:
    results: list[bool] = []
    from app.services.language_adaptive_intelligence.enums import AdaptiveDifficulty, ReviewHorizon
    from app.services.language_adaptive_intelligence.service import build_adaptive_bundle

    mastery, as_of = _fixture_mastery()
    progression = _fixture_progression()
    bundle = build_adaptive_bundle(
        student_id=7,
        language_id=1,
        mastery=mastery,
        progression=progression,
        as_of=as_of,
        force_enabled=True,
    )

    # Profile
    results.append(_ok("profile has weak topics", len(bundle.profile.weak_grammar_ids) >= 1))
    results.append(_ok("profile engagement set", bundle.profile.engagement_score >= 0))

    # Confidence model
    results.append(_ok("confidence views present", len(bundle.confidence_views) >= 1))
    pp_conf = next(v for v in bundle.confidence_views if v.grammar_id == "gram_present_perfect")
    results.append(
        _ok(
            "high mastery can pair with lower confidence",
            pp_conf.mastery_score > 0 and pp_conf.learning_confidence < 80.0,
        )
    )

    # Difficulty — grammar target unchanged
    results.append(_ok("difficulty grammar is current", bundle.difficulty is not None and bundle.difficulty.grammar_id == "gram_present_perfect"))
    results.append(
        _ok(
            "difficulty is enum level",
            bundle.difficulty is not None
            and bundle.difficulty.difficulty_level in AdaptiveDifficulty,
        )
    )

    # Review horizons only recommend
    horizons = {r.horizon for r in bundle.review_recommendations}
    results.append(_ok("uses review horizons", bool(horizons & set(ReviewHorizon))))

    # Activity mix boosts under-covered speaking
    results.append(_ok("speaking weight boosted", bundle.activity_mix.speaking >= 1.0))

    # Teacher / parent
    results.append(_ok("teacher struggling topics", len(bundle.teacher.struggling_topics) >= 1))
    results.append(_ok("parent percent in range", 0.0 <= bundle.parent.mastered_percent_band <= 100.0))
    results.append(_ok("parent focus set", bool(bundle.parent.current_focus)))
    results.append(_ok("parent minutes positive", bundle.parent.recommended_minutes >= 10))

    src = (ADAPTIVE_PKG / "recommendations.py").read_text(encoding="utf-8").lower()
    results.append(
        _ok(
            "recommendations never unlock",
            "never unlock" in src and "unlock grammar" not in src.replace("never unlocks grammar", ""),
        )
    )
    return results


def check_api_and_flags() -> list[bool]:
    results: list[bool] = []
    from app.core.config import Settings

    fields = Settings.model_fields
    results.append(_ok("flag LANG_ADAPTIVE_INTELLIGENCE_ENABLED", "LANG_ADAPTIVE_INTELLIGENCE_ENABLED" in fields))
    results.append(_ok("flag LANG_ADAPTIVE_PROFILE_PERSIST", "LANG_ADAPTIVE_PROFILE_PERSIST" in fields))
    results.append(
        _ok(
            "adaptive flag default false",
            fields["LANG_ADAPTIVE_INTELLIGENCE_ENABLED"].default is False,
        )
    )

    api = BACKEND / "app" / "api" / "language_adaptive_student.py"
    router = BACKEND / "app" / "api" / "router.py"
    results.append(_ok("API module exists", api.is_file()))
    router_text = router.read_text(encoding="utf-8")
    results.append(_ok("router includes adaptive", "language_adaptive_student" in router_text))

    for env_path in (BACKEND / ".env.example", BACKEND.parent / ".env.example"):
        if env_path.is_file():
            text = env_path.read_text(encoding="utf-8")
            results.append(_ok(f"{env_path.name} documents adaptive flag", "LANG_ADAPTIVE_INTELLIGENCE_ENABLED" in text))

    from app.services.language_grammar.ownership import (
        ADAPTIVE_INTELLIGENCE_PACKAGE,
        ADAPTIVE_JSONB_NAMESPACE_RESERVED,
    )

    results.append(_ok("ownership reserves adaptive package name", ADAPTIVE_INTELLIGENCE_PACKAGE == "language_adaptive_intelligence"))
    results.append(_ok("ownership reserves adaptive JSONB", ADAPTIVE_JSONB_NAMESPACE_RESERVED == "adaptive_intelligence"))
    return results


def check_storage_merge_isolation() -> list[bool]:
    results: list[bool] = []
    from app.services.language_adaptive_intelligence.storage import merge_adaptive_into_payload
    from app.services.language_adaptive_intelligence.types import ADAPTIVE_JSONB_NAMESPACE
    from app.services.language_grammar.ownership import GRAMMAR_JSONB_NAMESPACE

    payload = {
        GRAMMAR_JSONB_NAMESPACE: {
            "mastery": {"records": [{"grammar_id": "gram_present_simple"}]},
            "progression": {"current_grammar_id": "gram_present_perfect"},
        }
    }
    merged = merge_adaptive_into_payload(
        payload,
        {"learning_profile": {"student_id": 7, "preferred_pace": "steady"}},
    )
    results.append(
        _ok(
            "merge preserves grammar mastery",
            merged[GRAMMAR_JSONB_NAMESPACE]["mastery"] == payload[GRAMMAR_JSONB_NAMESPACE]["mastery"],
        )
    )
    results.append(
        _ok(
            "merge preserves grammar progression",
            merged[GRAMMAR_JSONB_NAMESPACE]["progression"]
            == payload[GRAMMAR_JSONB_NAMESPACE]["progression"],
        )
    )
    results.append(_ok("merge writes adaptive namespace", ADAPTIVE_JSONB_NAMESPACE in merged))
    return results


def main() -> int:
    print("Adaptive Learning Intelligence Phase 2 verification\n")
    suites = [
        ("Package shape", check_package_shape),
        ("Read-only isolation", check_read_only_isolation),
        ("Locked baselines untouched", check_locked_baselines_untouched),
        ("Deterministic recommendations", check_deterministic_recommendations),
        ("Explainability", check_explainability),
        ("Components", check_components),
        ("API and flags", check_api_and_flags),
        ("Storage merge isolation", check_storage_merge_isolation),
    ]
    all_ok = True
    for title, fn in suites:
        print(f"[{title}]")
        results = fn()
        if not all(results):
            all_ok = False
        print()
    if all_ok:
        print("ALL PHASE 2 CHECKS PASSED")
        return 0
    print("PHASE 2 CHECKS FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
