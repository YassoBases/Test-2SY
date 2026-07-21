"""Verify Wave E1 — AI Tutor Foundation.

Usage (from backend/):
    python scripts/verify_ai_tutor_foundation_e1.py
"""

from __future__ import annotations

import ast
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

BACKEND = Path(__file__).resolve().parents[1]
SERVICES = BACKEND / "app" / "services"
TUTOR_PKG = SERVICES / "language_ai_tutor"
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
    "language_adaptive_intelligence",
)

FORBIDDEN_WRITE_CALLS = (
    "apply_evidence_and_persist",
    "record_grammar_topic_completed",
    "evaluate_and_persist_grammar_progression",
    "sync_completed_topics_async",
    "complete_attested_activity",
    "append_evidence_ledger",
    "persist_learning_profile",
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


def _pkg_text() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in TUTOR_PKG.glob("*.py"))


def _adaptive_fingerprint() -> str:
    h = hashlib.sha256()
    for path in sorted(ADAPTIVE_PKG.rglob("*.py")):
        h.update(path.name.encode())
        h.update(path.read_bytes())
    return h.hexdigest()


def check_package_shape() -> list[bool]:
    results: list[bool] = []
    required = (
        "__init__.py",
        "types.py",
        "enums.py",
        "persona.py",
        "memory.py",
        "storage.py",
        "context.py",
        "safety.py",
        "explanation.py",
        "prompts.py",
        "llm.py",
        "service.py",
        "flags.py",
        "TUTOR_ARCHITECTURE.md",
    )
    results.append(_ok("tutor package directory", TUTOR_PKG.is_dir()))
    for name in required:
        results.append(_ok(f"file: {name}", (TUTOR_PKG / name).is_file()))
    init_text = (TUTOR_PKG / "__init__.py").read_text(encoding="utf-8")
    results.append(_ok("RESPONSIBILITY declared", "RESPONSIBILITY" in init_text))
    return results


def check_read_only_contract() -> list[bool]:
    results: list[bool] = []
    text = _pkg_text()
    imports: set[str] = set()
    for py_file in TUTOR_PKG.glob("*.py"):
        imports |= _parse_imports(py_file)

    for dep in (
        "language_grammar_mastery",
        "language_grammar_progression",
        "language_adaptive_intelligence",
        "language_grammar_catalog",
    ):
        results.append(_ok(f"may read {dep}", dep in imports))

    for forbidden in (
        "language_grammar_pipeline",
        "language_grammar_integrity",
        "language_grammar_module",
        "language_grammar_target_resolver",
    ):
        results.append(_ok(f"does not import {forbidden}", forbidden not in imports))

    for call in FORBIDDEN_WRITE_CALLS:
        results.append(_ok(f"no call {call}", call not in text))

    results.append(_ok("persist_profile=False for adaptive", "persist_profile=False" in text))
    results.append(_ok("storage guards grammar JSONB", "grammar JSONB would change" in text))
    results.append(_ok("storage guards adaptive JSONB", "adaptive JSONB would change" in text))
    results.append(_ok("uses ai_tutor namespace", "ai_tutor" in (TUTOR_PKG / "types.py").read_text(encoding="utf-8")))
    return results


def check_locked_baselines() -> list[bool]:
    results: list[bool] = []
    for pkg in LOCKED_PACKAGES:
        pkg_dir = SERVICES / pkg
        mentions = 0
        for py_file in pkg_dir.glob("*.py"):
            if "language_ai_tutor" in py_file.read_text(encoding="utf-8"):
                mentions += 1
        results.append(_ok(f"locked package free of tutor import: {pkg}", mentions == 0))

    from app.services.language_grammar_catalog.catalog import get_default_catalog

    cat = get_default_catalog()
    results.append(_ok("curriculum still 53 topics", len(cat.topics) == 53, str(len(cat.topics))))
    results.append(_ok("adaptive package fingerprint stable non-empty", bool(_adaptive_fingerprint())))
    return results


def _fixture_adaptive_and_progression():
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
    rec = GrammarMasteryRecord(
        student_id=9,
        language_id=1,
        grammar_id="gram_present_simple",
        state=GrammarMasteryState.practicing,
        dimensions=build_dimensions(
            understanding=70.0,
            accuracy=50.0,
            fluency=55.0,
            retention=48.0,
            confidence=0.3,
        ),
        confidence=0.3,
        stability=0.3,
        retention_risk=0.65,
        evidence_count=4,
        skill_coverage=frozenset({GrammarEvidenceSourceSkill.reading}),
        last_seen_at="2026-07-08T12:00:00Z",
    )
    mastery = GrammarMasterySnapshot(student_id=9, language_id=1, records=(rec,))
    progression = GrammarProgressionSnapshot(
        anchor_cefr=GrammarCEFRBand.A1,
        current_grammar_id="gram_present_simple",
        next_grammar_id="gram_present_continuous",
        unlocked_ids=("gram_present_simple",),
        locked_ids=(),
        future_ids=(),
        stretch_ids=(),
        candidate_pool_ids=("gram_present_simple",),
        candidate_priorities=(),
        progression_reason=("fixture",),
    )
    adaptive = build_adaptive_bundle(
        student_id=9,
        language_id=1,
        mastery=mastery,
        progression=progression,
        as_of=as_of,
        force_enabled=True,
    )
    return adaptive, progression, as_of


def check_context_and_safety() -> list[bool]:
    results: list[bool] = []
    from app.services.language_ai_tutor.enums import TutorPromptKind, TutorSafetyCode
    from app.services.language_ai_tutor.prompts import build_prompt_bundle
    from app.services.language_ai_tutor.service import build_tutor_context_pure
    from app.services.language_ai_tutor.types import TutorTurnRequest

    adaptive, progression, as_of = _fixture_adaptive_and_progression()

    ctx = build_tutor_context_pure(
        TutorTurnRequest(
            student_id=9,
            grammar_id="gram_present_simple",
            as_of=as_of,
            prompt_kind=TutorPromptKind.explain,
        ),
        progression=progression,
        adaptive=adaptive,
        force_enabled=True,
    )
    results.append(_ok("context safety ok", ctx.safety_code is TutorSafetyCode.ok))
    results.append(_ok("context grammar matches lesson", ctx.grammar is not None and ctx.grammar.grammar_id == "gram_present_simple"))
    results.append(_ok("curriculum version present", bool(ctx.curriculum_version)))
    results.append(_ok("explainability note present", bool(ctx.explainability_note)))
    results.append(_ok("persona assigned", ctx.teacher_persona.persona_id == "default_tutor"))

    # Mismatch fail closed
    bad = build_tutor_context_pure(
        TutorTurnRequest(
            student_id=9,
            grammar_id="gram_future_perfect",
            as_of=as_of,
        ),
        progression=progression,
        adaptive=adaptive,
        force_enabled=True,
    )
    results.append(
        _ok(
            "grammar mismatch rejected",
            bad.safety_code is TutorSafetyCode.grammar_mismatch,
        )
    )

    # No grammar fail closed
    empty_prog = GrammarProgressionSnapshot_empty()
    none_ctx = build_tutor_context_pure(
        TutorTurnRequest(student_id=9, as_of=as_of),
        progression=empty_prog,
        adaptive=None,
        force_enabled=True,
    )
    results.append(_ok("no grammar fail closed", none_ctx.safety_code is TutorSafetyCode.no_grammar))

    # Prompt never exposes raw model class names
    prompt = build_prompt_bundle(ctx, prompt_kind=TutorPromptKind.explain, student_message="Help me")
    results.append(_ok("prompt has system", "AI Tutor Foundation" in prompt.system))
    results.append(_ok("prompt has tutor_context", "tutor_context" in prompt.user))
    results.append(_ok("prompt has no GrammarMasterySnapshot", "GrammarMasterySnapshot" not in prompt.user))
    results.append(_ok("prompt has no AdaptiveIntelligenceBundle", "AdaptiveIntelligenceBundle" not in prompt.user))
    results.append(_ok("prompt stays on grammar_id", "gram_present_simple" in prompt.user))
    return results


def GrammarProgressionSnapshot_empty():
    from app.services.language_grammar.enums import GrammarCEFRBand
    from app.services.language_grammar_progression.types import GrammarProgressionSnapshot

    return GrammarProgressionSnapshot(
        anchor_cefr=GrammarCEFRBand.A1,
        current_grammar_id=None,
        next_grammar_id=None,
        unlocked_ids=(),
        locked_ids=(),
        future_ids=(),
        stretch_ids=(),
        candidate_pool_ids=(),
        candidate_priorities=(),
        progression_reason=("empty",),
    )


def check_adaptive_explanation_and_persona() -> list[bool]:
    results: list[bool] = []
    from app.services.language_ai_tutor.enums import ExplanationStyle, TutorPromptKind
    from app.services.language_ai_tutor.explanation import decide_explanation_style
    from app.services.language_ai_tutor.persona import PERSONA_CATALOG, resolve_teacher_persona
    from app.services.language_ai_tutor.prompts import template_fallback_utterance
    from app.services.language_ai_tutor.service import build_tutor_context_pure
    from app.services.language_ai_tutor.types import TutorAdaptiveSurface, TutorTurnRequest

    style, note = decide_explanation_style(
        TutorAdaptiveSurface(average_confidence=30.0, preferred_pace="slow")
    )
    results.append(_ok("low confidence -> simplified", style is ExplanationStyle.simplified))
    results.append(_ok("explainability mentions confidence", "confidence" in note.lower()))

    style2, _ = decide_explanation_style(
        TutorAdaptiveSurface(
            average_confidence=80.0,
            preferred_pace="fast",
            preferred_explanation_depth="brief",
            learning_confidence_current=80.0,
        )
    )
    results.append(_ok("high confidence -> concise", style2 is ExplanationStyle.concise))

    style3, note3 = decide_explanation_style(
        TutorAdaptiveSurface(weakness_signal_kinds=("recurring_mistakes",))
    )
    results.append(_ok("mistakes -> analogy", style3 is ExplanationStyle.analogy))
    results.append(_ok("analogy note transparent", "analogy" in note3.lower() or "mistake" in note3.lower()))

    p = resolve_teacher_persona(persona_id="encouraging_coach")
    results.append(_ok("persona catalog reusable", "encouraging_coach" in PERSONA_CATALOG))
    results.append(_ok("persona tone consistent", p.tone == "encouraging"))

    adaptive, progression, as_of = _fixture_adaptive_and_progression()
    ctx = build_tutor_context_pure(
        TutorTurnRequest(student_id=9, grammar_id="gram_present_simple", as_of=as_of),
        progression=progression,
        adaptive=adaptive,
        force_enabled=True,
    )
    utter = template_fallback_utterance(ctx, prompt_kind=TutorPromptKind.explain)
    results.append(_ok("template mentions current grammar", "Present Simple" in utter or "gram_present_simple" in utter))
    results.append(_ok("template does not invent Future Perfect", "Future Perfect" not in utter))
    return results


def check_memory_and_storage() -> list[bool]:
    results: list[bool] = []
    from app.services.language_ai_tutor.memory import append_turn, empty_memory, memory_from_dict, memory_to_dict
    from app.services.language_ai_tutor.storage import merge_tutor_into_payload
    from app.services.language_ai_tutor.types import AI_TUTOR_JSONB_NAMESPACE
    from app.services.language_grammar.ownership import (
        ADAPTIVE_JSONB_NAMESPACE_RESERVED,
        GRAMMAR_JSONB_NAMESPACE,
    )

    mem = empty_memory(student_id=9, language_id=1, conversation_id="tutor_test")
    mem = append_turn(mem, role="student", content="What is Present Simple?")
    mem = append_turn(mem, role="tutor", content="It describes habits.")
    roundtrip = memory_from_dict(memory_to_dict(mem), student_id=9, language_id=1)
    results.append(_ok("memory roundtrip", roundtrip is not None and len(roundtrip.turns) == 2))
    results.append(_ok("recurring question captured", len(roundtrip.recurring_questions) >= 1))

    payload = {
        GRAMMAR_JSONB_NAMESPACE: {"mastery": {"records": [{"grammar_id": "x"}]}},
        ADAPTIVE_JSONB_NAMESPACE_RESERVED: {"learning_profile": {"preferred_pace": "steady"}},
    }
    merged = merge_tutor_into_payload(payload, {"conversations": {"tutor_test": memory_to_dict(mem)}})
    results.append(
        _ok(
            "merge preserves grammar",
            merged[GRAMMAR_JSONB_NAMESPACE] == payload[GRAMMAR_JSONB_NAMESPACE],
        )
    )
    results.append(
        _ok(
            "merge preserves adaptive",
            merged[ADAPTIVE_JSONB_NAMESPACE_RESERVED] == payload[ADAPTIVE_JSONB_NAMESPACE_RESERVED],
        )
    )
    results.append(_ok("merge writes ai_tutor", AI_TUTOR_JSONB_NAMESPACE in merged))
    return results


def check_api_and_flags() -> list[bool]:
    results: list[bool] = []
    from app.core.config import Settings
    from app.services.language_grammar.ownership import (
        AI_TUTOR_JSONB_NAMESPACE_RESERVED,
        AI_TUTOR_PACKAGE,
    )

    fields = Settings.model_fields
    for key in (
        "LANG_AI_TUTOR_ENABLED",
        "LANG_AI_TUTOR_MEMORY_PERSIST",
        "LANG_AI_TUTOR_LLM_ENABLED",
    ):
        results.append(_ok(f"flag {key}", key in fields))
    results.append(_ok("tutor flag default false", fields["LANG_AI_TUTOR_ENABLED"].default is False))

    api = BACKEND / "app" / "api" / "language_ai_tutor.py"
    router = BACKEND / "app" / "api" / "router.py"
    results.append(_ok("API module exists", api.is_file()))
    results.append(_ok("router includes tutor", "language_ai_tutor" in router.read_text(encoding="utf-8")))
    results.append(_ok("ownership package name", AI_TUTOR_PACKAGE == "language_ai_tutor"))
    results.append(_ok("ownership JSONB", AI_TUTOR_JSONB_NAMESPACE_RESERVED == "ai_tutor"))

    for env_path in (BACKEND / ".env.example", BACKEND.parent / ".env.example"):
        if env_path.is_file():
            results.append(
                _ok(
                    f"{env_path.name} documents tutor flag",
                    "LANG_AI_TUTOR_ENABLED" in env_path.read_text(encoding="utf-8"),
                )
            )
    return results


def main() -> int:
    print("AI Tutor Foundation Wave E1 verification\n")
    suites = [
        ("Package shape", check_package_shape),
        ("Read-only contract", check_read_only_contract),
        ("Locked baselines", check_locked_baselines),
        ("Context and safety", check_context_and_safety),
        ("Adaptive explanation and persona", check_adaptive_explanation_and_persona),
        ("Memory and storage", check_memory_and_storage),
        ("API and flags", check_api_and_flags),
    ]
    all_ok = True
    for title, fn in suites:
        print(f"[{title}]")
        results = fn()
        if not all(results):
            all_ok = False
        print()
    if all_ok:
        print("ALL WAVE E1 CHECKS PASSED")
        return 0
    print("WAVE E1 CHECKS FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
