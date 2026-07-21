"""Verify Grammar Speaking Domain Framework V1.2A.

Usage (from backend/):
    python scripts/verify_speaking_v12a_domain.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

BACKEND = Path(__file__).resolve().parents[1]
SERVICES = BACKEND / "app" / "services"
PKG = SERVICES / "language_grammar_speaking"

FORBIDDEN = frozenset(
    {
        "claude_service",
        "language_grammar_lesson_runtime",
        "language_grammar_lesson_planner",
        "language_grammar_activity_provider",
        "language_grammar_mastery",
        "language_grammar_progression",
        "language_grammar_review",
        "language_speaking_lesson_runtime",
        "language_speaking_journey",
    }
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


def _pkg_imports() -> set[str]:
    deps: set[str] = set()
    for py in PKG.rglob("*.py"):
        deps |= _parse_imports(py)
    deps.discard("language_grammar_speaking")
    return deps


def _context():
    from app.services.language_grammar_speaking import SpeakingContext

    return SpeakingContext(
        student_id=1,
        language_id=1,
        activity_id="act_voice_1",
        grammar_targets=("gram_present_simple",),
        locale="en",
        lesson_id="gless_1",
    )


def audit_1_domain_integrity() -> list[bool]:
    print("[Audit 1 - Domain Integrity]")
    results: list[bool] = []
    from app.services.language_grammar_speaking import (
        SpeakingAttempt,
        SpeakingContext,
        SpeakingEvidence,
        SpeakingResult,
        SpeakingSession,
        SpeakingState,
        SpeakingTurn,
        initialize,
        validate_grammar_targets,
        validate_session_state,
    )

    for name, cls in (
        ("SpeakingSession", SpeakingSession),
        ("SpeakingAttempt", SpeakingAttempt),
        ("SpeakingTurn", SpeakingTurn),
        ("SpeakingResult", SpeakingResult),
        ("SpeakingEvidence", SpeakingEvidence),
        ("SpeakingContext", SpeakingContext),
    ):
        results.append(_ok(f"model {name}", cls is not None))

    ctx = _context()
    state = initialize(ctx, at="2026-01-01T00:00:00Z", session_id="sspeak_test")
    results.append(_ok("SpeakingState created", isinstance(state, SpeakingState)))
    session = state.session
    results.append(_ok("session_id", bool(session.session_id)))
    results.append(_ok("activity_id", session.activity_id == ctx.activity_id))
    results.append(_ok("student_id", session.student_id == 1))
    results.append(_ok("grammar_targets", session.grammar_targets == ("gram_present_simple",)))
    results.append(_ok("status initialized", session.status.value == "initialized"))
    results.append(_ok("created_at/updated_at", bool(session.created_at and session.updated_at)))
    try:
        validate_session_state(session)
        results.append(_ok("session validates", True))
    except Exception as exc:  # noqa: BLE001
        results.append(_ok("session validates", False, str(exc)))

    try:
        validate_grammar_targets(())
        results.append(_ok("empty grammar_targets rejected", False))
    except Exception:
        results.append(_ok("empty grammar_targets rejected", True))

    results.append(_ok("Audit 1 verdict", all(results)))
    print()
    return results


def audit_2_lifecycle() -> list[bool]:
    print("[Audit 2 - Lifecycle]")
    results: list[bool] = []
    from app.services.language_grammar_speaking import (
        SpeakingLifecyclePhase,
        cancel,
        complete_session,
        finish_attempt,
        initialize,
        next_turn,
        run_happy_path,
        start_attempt,
        start_session,
    )

    ctx = _context()
    state = initialize(ctx, at="t0")
    state = start_session(state, at="t1")
    state = start_attempt(state, at="t2")
    state = next_turn(state, prompt_reference="p1", at="t3")
    state = next_turn(state, prompt_reference="p2", student_response_reference="r2", at="t4")
    state = finish_attempt(state, at="t5")
    state = complete_session(state, at="t6")

    phases = set(state.phases_completed)
    for phase in SpeakingLifecyclePhase:
        if phase is SpeakingLifecyclePhase.cancel:
            continue
        results.append(_ok(f"phase {phase.value}", phase.value in phases))

    results.append(_ok("session completed", state.session.status.value == "completed"))
    results.append(_ok("attempt finished", state.session.attempts[-1].status.value == "finished"))
    results.append(_ok("turns present", len(state.session.attempts[-1].turns) == 2))

    # Cancel path
    s2 = initialize(ctx, at="c0", session_id="sspeak_cancel")
    s2 = start_session(s2, at="c1")
    s2 = cancel(s2, reason="user", at="c2")
    results.append(_ok("cancel lifecycle", s2.session.status.value == "cancelled"))
    results.append(_ok("cancel phase recorded", SpeakingLifecyclePhase.cancel.value in s2.phases_completed))

    happy = run_happy_path(ctx, at="2026-01-01T00:00:00Z", turns=3)
    results.append(_ok("happy path completes", happy.session.status.value == "completed"))
    results.append(_ok("Audit 2 verdict", all(results)))
    print()
    return results


def audit_3_state_machine() -> list[bool]:
    print("[Audit 3 - State Machine]")
    results: list[bool] = []
    from app.services.language_grammar_speaking import (
        SpeakingSessionStatus,
        SpeakingStateError,
        assert_session_transition,
        complete_session,
        finish_attempt,
        initialize,
        start_attempt,
        start_session,
    )

    # Legal
    try:
        assert_session_transition(SpeakingSessionStatus.initialized, SpeakingSessionStatus.active)
        results.append(_ok("legal initialized->active", True))
    except SpeakingStateError:
        results.append(_ok("legal initialized->active", False))

    # Illegal
    try:
        assert_session_transition(SpeakingSessionStatus.completed, SpeakingSessionStatus.active)
        results.append(_ok("illegal completed->active rejected", False))
    except SpeakingStateError:
        results.append(_ok("illegal completed->active rejected", True))

    ctx = _context()
    state = initialize(ctx, at="s0")
    state = start_session(state, at="s1")
    try:
        complete_session(state, at="s2")
        results.append(_ok("complete without result rejected", False))
    except Exception:
        results.append(_ok("complete without result rejected", True))

    state = start_attempt(state, at="s3")
    try:
        complete_session(state, at="s4")
        results.append(_ok("complete with active attempt rejected", False))
    except Exception:
        results.append(_ok("complete with active attempt rejected", True))

    state = finish_attempt(state, at="s5")
    state = complete_session(state, at="s6")
    results.append(_ok("legal complete after finish", state.session.status.value == "completed"))
    results.append(_ok("Audit 3 verdict", all(results)))
    print()
    return results


def audit_4_evidence_mapping() -> list[bool]:
    print("[Audit 4 - Evidence Mapping]")
    results: list[bool] = []
    from app.services.language_grammar_evidence.types import GrammarEvidenceObservation
    from app.services.language_grammar_speaking import (
        map_session_result_to_observations,
        map_speaking_evidence_to_observations,
        run_happy_path,
        to_view,
    )

    ctx = _context()
    state = run_happy_path(ctx, at="2026-01-01T00:00:00Z")
    results.append(_ok("session has SpeakingEvidence", len(state.session.evidence) >= 1))
    results.append(_ok("session has SpeakingResult", state.session.result is not None))

    obs = map_session_result_to_observations(state.session, context=ctx, observed_at="2026-01-01T00:00:00Z")
    results.append(_ok("maps to observations", len(obs) >= 1))
    results.append(_ok("observation type", isinstance(obs[0], GrammarEvidenceObservation)))
    results.append(_ok("source_skill speaking", obs[0].source_skill.value == "speaking"))
    results.append(_ok("grammar_id preserved", obs[0].grammar_id == "gram_present_simple"))
    results.append(_ok("no mastery fields written", not hasattr(obs[0], "overall_mastery")))

    view = to_view(state)
    results.append(_ok("view includes mapped_observations", len(view.mapped_observations) >= 1))

    # Adapter does not call mastery write APIs
    src = (PKG / "evidence.py").read_text(encoding="utf-8")
    results.append(
        _ok(
            "evidence module has no mastery write",
            "apply_evidence_and_persist" not in src
            and "apply_evidence_batch" not in src
            and "update_mastery" not in src
            and "language_grammar_mastery" not in src,
        )
    )
    results.append(_ok("Audit 4 verdict", all(results)))
    print()
    return results


def audit_5_llm_isolation() -> list[bool]:
    print("[Audit 5 - Isolation from LLM]")
    results: list[bool] = []
    src = "\n".join(p.read_text(encoding="utf-8") for p in PKG.rglob("*.py"))
    lowered = src.lower()
    for needle in (
        "anthropic",
        "openai",
        "gemini",
        "claude_service",
        "speech_to_text",
        "text_to_speech",
        "whisper",
        "deepgram",
        "import httpx",
        "prompt_template",
    ):
        results.append(_ok(f"no {needle}", needle not in lowered))

    # AST: no imports of LLM/audio SDKs
    for py in PKG.rglob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                modules = []
                if isinstance(node, ast.Import):
                    modules = [a.name for a in node.names]
                elif node.module:
                    modules = [node.module]
                for mod in modules:
                    root = mod.split(".")[0]
                    results.append(
                        _ok(
                            f"{py.name} no sdk {root}",
                            root
                            not in {
                                "anthropic",
                                "openai",
                                "google",
                                "whisper",
                                "deepgram",
                                "httpx",
                            },
                        )
                    )

    deps = _pkg_imports()
    for bad in sorted(FORBIDDEN):
        results.append(_ok(f"no import {bad}", bad not in deps))

    results.append(_ok("Audit 5 verdict", all(results)))
    print()
    return results


def audit_6_architecture() -> list[bool]:
    print("[Audit 6 - Architecture]")
    results: list[bool] = []
    from app.services.language_grammar.ownership import (
        ALLOWED_PACKAGE_DEPENDENCIES,
        FORBIDDEN_MASTERY_WRITERS,
        PACKAGE_LAYER,
        PACKAGE_OWNERSHIP,
    )

    results.append(_ok("ownership entry", "language_grammar_speaking" in PACKAGE_OWNERSHIP))
    results.append(_ok("layer skill_domain", PACKAGE_LAYER.get("language_grammar_speaking") == "skill_domain"))
    results.append(
        _ok(
            "forbidden mastery writer",
            "language_grammar_speaking" in FORBIDDEN_MASTERY_WRITERS,
        )
    )

    allowed = ALLOWED_PACKAGE_DEPENDENCIES.get("language_grammar_speaking", frozenset())
    deps = {d for d in _pkg_imports() if d.startswith("language_grammar")}
    deps.discard("language_grammar")  # shared infra
    extra = deps - set(allowed)
    results.append(_ok("DAG respected", not extra, str(sorted(extra))))
    results.append(_ok("may depend on evidence", "language_grammar_evidence" in allowed))

    # skill_executor may depend on speaking (allowed edge)
    se_allowed = ALLOWED_PACKAGE_DEPENDENCIES.get("language_grammar_skill_executor", frozenset())
    results.append(_ok("skill_executor may depend on speaking", "language_grammar_speaking" in se_allowed))

    results.append(_ok("types.py present", (PKG / "types.py").is_file()))
    results.append(_ok("no engine.py", not (PKG / "engine.py").is_file()))
    init = (PKG / "__init__.py").read_text(encoding="utf-8")
    results.append(_ok("RESPONSIBILITY declared", "RESPONSIBILITY" in init))
    results.append(_ok("Audit 6 verdict", all(results)))
    print()
    return results


def check_flags_and_contracts() -> list[bool]:
    print("[Flags & contracts]")
    results: list[bool] = []
    from app.core.config import get_settings
    from app.services.language_grammar_speaking import (
        SPEAKING_DOMAIN_SCHEMA_VERSION,
        speaking_domain_enabled,
    )

    settings = get_settings()
    results.append(
        _ok(
            "LANG_GRAMMAR_SPEAKING_DOMAIN_ENABLED defined",
            hasattr(settings, "LANG_GRAMMAR_SPEAKING_DOMAIN_ENABLED"),
        )
    )
    results.append(_ok("speaking_domain_enabled readable", isinstance(speaking_domain_enabled(), bool)))
    results.append(_ok("schema version v1", SPEAKING_DOMAIN_SCHEMA_VERSION == 1))

    env = (BACKEND.parent / ".env.example").read_text(encoding="utf-8")
    results.append(_ok(".env.example documents flag", "LANG_GRAMMAR_SPEAKING_DOMAIN_ENABLED" in env))
    print()
    return results


def main() -> int:
    print("Grammar Speaking Domain V1.2A verification\n")
    all_results: list[bool] = []
    all_results.extend(audit_1_domain_integrity())
    all_results.extend(audit_2_lifecycle())
    all_results.extend(audit_3_state_machine())
    all_results.extend(audit_4_evidence_mapping())
    all_results.extend(audit_5_llm_isolation())
    all_results.extend(audit_6_architecture())
    all_results.extend(check_flags_and_contracts())

    passed = sum(1 for r in all_results if r)
    failed = sum(1 for r in all_results if not r)
    print(f"Summary: {passed} passed, {failed} failed, {len(all_results)} total")
    if failed:
        print("V1.2A VERDICT: NOT READY")
        return 1
    print("V1.2A VERDICT: READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
