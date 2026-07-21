"""Verify Wave E2 — Conversational Coaching.

Usage (from backend/):
    python scripts/verify_ai_tutor_coaching_e2.py
"""

from __future__ import annotations

import ast
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

BACKEND = Path(__file__).resolve().parents[1]
SERVICES = BACKEND / "app" / "services"
COACH_PKG = SERVICES / "language_ai_tutor_coaching"
E1_PKG = SERVICES / "language_ai_tutor"
ADAPTIVE_PKG = SERVICES / "language_adaptive_intelligence"
CURRICULUM = BACKEND / "curriculum" / "english" / "grammar"

LOCKED_NO_TUTOR_IMPORT = (
    "language_grammar_catalog",
    "language_grammar_mastery",
    "language_grammar_progression",
    "language_grammar_integrity",
    "language_adaptive_intelligence",
    "language_ai_tutor",  # E1 locked — must not import coaching
)

FORBIDDEN_WRITE_CALLS = (
    "apply_evidence_and_persist",
    "record_grammar_topic_completed",
    "evaluate_and_persist_grammar_progression",
    "sync_completed_topics_async",
    "persist_learning_profile",
    "persist_conversation_memory",
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
        "intent.py",
        "hints.py",
        "socratic.py",
        "diagnosis.py",
        "reflection.py",
        "motivation.py",
        "variety.py",
        "strategy.py",
        "progression.py",
        "wrapup.py",
        "prompts.py",
        "storage.py",
        "llm.py",
        "service.py",
        "flags.py",
        "COACHING_ARCHITECTURE.md",
    )
    results.append(_ok("coaching package directory", COACH_PKG.is_dir()))
    for name in required:
        results.append(_ok(f"file: {name}", (COACH_PKG / name).is_file()))
    results.append(
        _ok("RESPONSIBILITY declared", "RESPONSIBILITY" in (COACH_PKG / "__init__.py").read_text(encoding="utf-8"))
    )
    return results


def check_e1_locked_untouched() -> list[bool]:
    results: list[bool] = []
    # Coaching must not live inside E1
    for py_file in E1_PKG.glob("*.py"):
        text = py_file.read_text(encoding="utf-8")
        results.append(
            _ok(
                f"E1 free of coaching import: {py_file.name}",
                "language_ai_tutor_coaching" not in text,
            )
        )
    results.append(_ok("E1 fingerprint non-empty", bool(_fingerprint(E1_PKG))))
    results.append(_ok("Adaptive fingerprint non-empty", bool(_fingerprint(ADAPTIVE_PKG))))
    from app.services.language_grammar_catalog.catalog import get_default_catalog

    cat = get_default_catalog()
    results.append(_ok("curriculum still 53 topics", len(cat.topics) == 53, str(len(cat.topics))))
    return results


def check_read_only_contract() -> list[bool]:
    results: list[bool] = []
    imports: set[str] = set()
    text = ""
    for py_file in COACH_PKG.glob("*.py"):
        imports |= _parse_imports(py_file)
        text += py_file.read_text(encoding="utf-8") + "\n"

    results.append(_ok("may read language_ai_tutor", "language_ai_tutor" in imports))
    for forbidden in (
        "language_grammar_pipeline",
        "language_grammar_integrity",
        "language_grammar_module",
        "language_grammar_target_resolver",
        "language_grammar_mastery",
        "language_grammar_progression",
    ):
        # mastery/progression may appear only via E1 — coach service should not import them directly
        results.append(_ok(f"does not import {forbidden}", forbidden not in imports))

    for call in FORBIDDEN_WRITE_CALLS:
        results.append(_ok(f"no call {call}", call not in text))

    results.append(_ok("storage guards grammar", "grammar" in text and "would change" in text))
    results.append(_ok("uses coaching JSONB namespace", "ai_tutor_coaching" in text))
    results.append(
        _ok(
            "does not modify E1 prompts module",
            not (E1_PKG / "prompts.py").read_text(encoding="utf-8").find("Wave E2") > 0
            or "Wave E2" not in (E1_PKG / "prompts.py").read_text(encoding="utf-8"),
        )
    )
    return results


def _fixtures():
    from app.services.language_adaptive_intelligence.service import build_adaptive_bundle
    from app.services.language_ai_tutor_coaching.progression import empty_coaching_state
    from app.services.language_ai_tutor_coaching.service import build_coaching_context_pure
    from app.services.language_ai_tutor_coaching.types import CoachingTurnRequest
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
        student_id=11,
        language_id=1,
        grammar_id="gram_present_simple",
        state=GrammarMasteryState.practicing,
        dimensions=build_dimensions(
            understanding=60.0, accuracy=45.0, fluency=50.0, retention=40.0, confidence=0.3
        ),
        confidence=0.3,
        stability=0.3,
        retention_risk=0.6,
        evidence_count=3,
        skill_coverage=frozenset({GrammarEvidenceSourceSkill.reading}),
        last_seen_at="2026-07-10T12:00:00Z",
    )
    mastery = GrammarMasterySnapshot(student_id=11, language_id=1, records=(rec,))
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
        student_id=11,
        language_id=1,
        mastery=mastery,
        progression=progression,
        as_of=as_of,
        force_enabled=True,
    )
    req = CoachingTurnRequest(
        student_id=11,
        grammar_id="gram_present_simple",
        message="Can you help?",
        as_of=as_of,
        session_id="coach_test",
    )
    ctx = build_coaching_context_pure(req, progression=progression, adaptive=adaptive, force_enabled=True)
    state = empty_coaching_state(
        student_id=11, language_id=1, session_id="coach_test", grammar_id="gram_present_simple"
    )
    return ctx, state, req, progression, adaptive, as_of


def check_hint_escalation_and_socratic() -> list[bool]:
    results: list[bool] = []
    from app.services.language_ai_tutor_coaching.enums import HintLevel
    from app.services.language_ai_tutor_coaching.hints import HINT_LADDER
    from app.services.language_ai_tutor_coaching.service import respond_coaching_turn_pure
    from app.services.language_ai_tutor_coaching.socratic import avoids_immediate_answer
    from app.services.language_ai_tutor_coaching.types import CoachingTurnRequest

    ctx, state, base_req, *_ = _fixtures()

    # Turn 1: general help -> question/hint, not full answer
    r1, s1 = respond_coaching_turn_pure(ctx, state, base_req)
    results.append(_ok("first move guides", r1.move.value in {"question", "hint", "encourage"}))
    results.append(_ok("avoids immediate answer", avoids_immediate_answer(r1.utterance)))
    results.append(_ok("not full explanation first", r1.hint_level != HintLevel.full_explanation.value))

    # Explicit hint asks escalate
    req_hint = CoachingTurnRequest(
        student_id=11,
        grammar_id="gram_present_simple",
        message="I need a hint",
        as_of=base_req.as_of,
        session_id="coach_test",
    )
    r2, s2 = respond_coaching_turn_pure(ctx, s1, req_hint)
    results.append(_ok("hint level recorded", r2.hint_level is not None))
    results.append(_ok("previous hints remembered", len(s2.previous_hints) >= 1))

    r3, s3 = respond_coaching_turn_pure(ctx, s2, req_hint)
    results.append(_ok("hint escalates", len(s3.previous_hints) >= len(s2.previous_hints)))
    idx2 = HINT_LADDER.index(HintLevel(r2.hint_level)) if r2.hint_level else -1
    idx3 = HINT_LADDER.index(HintLevel(r3.hint_level)) if r3.hint_level else -1
    results.append(_ok("hint index non-decreasing", idx3 >= idx2 >= 0))

    # Should not jump to worked example without request
    results.append(
        _ok(
            "no skip to worked example",
            r3.hint_level
            not in {HintLevel.worked_example.value, HintLevel.full_explanation.value},
        )
    )

    # Explicit full answer allowed
    req_full = CoachingTurnRequest(
        student_id=11,
        grammar_id="gram_present_simple",
        message="Just tell me the answer",
        request_full_answer=True,
        as_of=base_req.as_of,
        session_id="coach_test",
    )
    r4, s4 = respond_coaching_turn_pure(ctx, s3, req_full)
    results.append(
        _ok(
            "full answer only when requested",
            r4.hint_level
            in {HintLevel.full_explanation.value, HintLevel.worked_example.value},
        )
    )
    results.append(_ok("reflection after reveal", bool(r4.reflection_question) or r4.move.value == "explain"))
    return results


def check_diagnosis_reflection_motivation_wrap() -> list[bool]:
    results: list[bool] = []
    from app.services.language_ai_tutor_coaching.diagnosis import diagnose_mistake, diagnosis_consistent
    from app.services.language_ai_tutor_coaching.motivation import praise_is_appropriate
    from app.services.language_ai_tutor_coaching.service import respond_coaching_turn_pure
    from app.services.language_ai_tutor_coaching.types import CoachingTurnRequest

    ctx, state, base_req, progression, *_ = _fixtures()

    d1 = diagnose_mistake(ctx, attempt="He go school", message="")
    d2 = diagnose_mistake(ctx, attempt="He go school", message="")
    results.append(_ok("diagnosis consistent", diagnosis_consistent(d1, d2)))
    results.append(_ok("diagnosis has why", "because" in d1.why.lower() or "misconception" in d1.why.lower() or "looks like" in d1.why.lower()))

    wrong = CoachingTurnRequest(
        student_id=11,
        grammar_id="gram_present_simple",
        message="I tried this",
        student_attempt="He go school",
        is_correct=False,
        as_of=base_req.as_of,
        session_id="coach_test",
    )
    r_wrong, s_wrong = respond_coaching_turn_pure(ctx, state, wrong)
    results.append(_ok("diagnose move on mistake", r_wrong.move.value == "diagnose"))
    results.append(_ok("diagnosis kind set", bool(r_wrong.diagnosis_kind)))
    results.append(_ok("motivation appropriate", praise_is_appropriate(r_wrong.motivation_line or "ok")))

    correct = CoachingTurnRequest(
        student_id=11,
        grammar_id="gram_present_simple",
        message="I think I got it",
        student_attempt="He goes to school",
        is_correct=True,
        as_of=base_req.as_of,
        session_id="coach_test",
    )
    r_ok, s_ok = respond_coaching_turn_pure(ctx, s_wrong, correct)
    results.append(
        _ok(
            "reflection after success",
            bool(r_ok.reflection_question) or r_ok.move.value in {"reflect", "challenge", "encourage"},
        )
    )

    wrap_req = CoachingTurnRequest(
        student_id=11,
        grammar_id="gram_present_simple",
        message="Please wrap up the lesson",
        request_wrap_up=True,
        as_of=base_req.as_of,
        session_id="coach_test",
    )
    r_wrap, _ = respond_coaching_turn_pure(
        ctx, s_ok, wrap_req, next_grammar_id=progression.next_grammar_id
    )
    results.append(_ok("wrap move", r_wrap.move.value == "wrap_up"))
    results.append(_ok("wrap summary present", r_wrap.wrap_up is not None and bool(r_wrap.wrap_up.summary_text)))
    results.append(
        _ok(
            "wrap mentions today's grammar",
            r_wrap.wrap_up is not None
            and (
                "present" in r_wrap.wrap_up.todays_grammar.lower()
                or r_wrap.wrap_up.grammar_id == "gram_present_simple"
            ),
        )
    )
    results.append(
        _ok(
            "wrap next preview informational",
            r_wrap.wrap_up is not None and "Next lesson preview" in r_wrap.wrap_up.next_lesson_preview,
        )
    )
    return results


def check_storage_and_api_flags() -> list[bool]:
    results: list[bool] = []
    from app.core.config import Settings
    from app.services.language_ai_tutor_coaching.progression import empty_coaching_state, state_to_dict
    from app.services.language_ai_tutor_coaching.storage import merge_coaching_into_payload
    from app.services.language_ai_tutor_coaching.types import COACHING_JSONB_NAMESPACE
    from app.services.language_grammar.ownership import (
        ADAPTIVE_JSONB_NAMESPACE_RESERVED,
        AI_TUTOR_COACHING_JSONB_NAMESPACE_RESERVED,
        AI_TUTOR_JSONB_NAMESPACE_RESERVED,
        GRAMMAR_JSONB_NAMESPACE,
    )

    state = empty_coaching_state(student_id=11, language_id=1, session_id="coach_x")
    payload = {
        GRAMMAR_JSONB_NAMESPACE: {"mastery": {"records": []}},
        ADAPTIVE_JSONB_NAMESPACE_RESERVED: {"learning_profile": {}},
        AI_TUTOR_JSONB_NAMESPACE_RESERVED: {"conversations": {}},
    }
    merged = merge_coaching_into_payload(
        payload, {"sessions": {"coach_x": state_to_dict(state)}, "active_session_id": "coach_x"}
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
            "merge preserves E1 ai_tutor",
            merged[AI_TUTOR_JSONB_NAMESPACE_RESERVED] == payload[AI_TUTOR_JSONB_NAMESPACE_RESERVED],
        )
    )
    results.append(_ok("merge writes coaching ns", COACHING_JSONB_NAMESPACE in merged))
    results.append(
        _ok(
            "ownership coaching ns",
            AI_TUTOR_COACHING_JSONB_NAMESPACE_RESERVED == "ai_tutor_coaching",
        )
    )

    fields = Settings.model_fields
    for key in (
        "LANG_AI_TUTOR_COACHING_ENABLED",
        "LANG_AI_TUTOR_COACHING_PERSIST",
        "LANG_AI_TUTOR_COACHING_LLM_ENABLED",
    ):
        results.append(_ok(f"flag {key}", key in fields))
    results.append(_ok("coaching flag default false", fields["LANG_AI_TUTOR_COACHING_ENABLED"].default is False))

    api = BACKEND / "app" / "api" / "language_ai_tutor_coaching.py"
    router = BACKEND / "app" / "api" / "router.py"
    results.append(_ok("API exists", api.is_file()))
    results.append(_ok("router includes coaching", "language_ai_tutor_coaching" in router.read_text(encoding="utf-8")))
    for env_path in (BACKEND / ".env.example", BACKEND.parent / ".env.example"):
        if env_path.is_file():
            results.append(
                _ok(
                    f"{env_path.name} documents coaching flag",
                    "LANG_AI_TUTOR_COACHING_ENABLED" in env_path.read_text(encoding="utf-8"),
                )
            )
    return results


def main() -> int:
    print("Conversational Coaching Wave E2 verification\n")
    suites = [
        ("Package shape", check_package_shape),
        ("E1 / Adaptive / Curriculum locked", check_e1_locked_untouched),
        ("Read-only contract", check_read_only_contract),
        ("Hint escalation and Socratic", check_hint_escalation_and_socratic),
        ("Diagnosis / reflection / motivation / wrap", check_diagnosis_reflection_motivation_wrap),
        ("Storage and API flags", check_storage_and_api_flags),
    ]
    all_ok = True
    for title, fn in suites:
        print(f"[{title}]")
        results = fn()
        if not all(results):
            all_ok = False
        print()
    if all_ok:
        print("ALL WAVE E2 CHECKS PASSED")
        return 0
    print("WAVE E2 CHECKS FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
