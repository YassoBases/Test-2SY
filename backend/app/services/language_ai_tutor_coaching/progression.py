"""Conversation progression — remember hints/mistakes; escalate; avoid repeats."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone

from app.services.language_ai_tutor_coaching.enums import HintLevel
from app.services.language_ai_tutor_coaching.hints import HINT_LADDER, clamp_hint_index
from app.services.language_ai_tutor_coaching.types import (
    CoachingDecision,
    CoachingSessionState,
    MistakeDiagnosis,
)

MAX_HINT_HISTORY = 12
MAX_EXPL_HISTORY = 8
MAX_MISTAKE_HISTORY = 8


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_session_id() -> str:
    return f"coach_{uuid.uuid4().hex[:16]}"


def empty_coaching_state(
    *,
    student_id: int,
    language_id: int,
    session_id: str | None = None,
    grammar_id: str = "",
    activity_id: str = "",
) -> CoachingSessionState:
    return CoachingSessionState(
        student_id=student_id,
        language_id=language_id,
        session_id=session_id or new_session_id(),
        grammar_id=grammar_id,
        activity_id=activity_id,
        updated_at=_now(),
    )


def utterance_fingerprint(text: str) -> str:
    normalized = " ".join(text.lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def would_repeat_explanation(state: CoachingSessionState, utterance: str) -> bool:
    fp = utterance_fingerprint(utterance)
    if fp and fp == state.last_utterance_fingerprint:
        return True
    return utterance.strip() in state.previous_explanations


def vary_if_repeat(state: CoachingSessionState, utterance: str) -> str:
    """If identical to last explanation, append a fresh angle (never identical dump)."""
    if not would_repeat_explanation(state, utterance):
        return utterance
    return (
        utterance.rstrip()
        + " Let's try a different angle: focus on the time meaning before the verb form."
    )


def apply_decision_to_state(
    state: CoachingSessionState,
    decision: CoachingDecision,
    *,
    utterance: str,
    hint_text: str | None = None,
    diagnosis: MistakeDiagnosis | None = None,
) -> CoachingSessionState:
    hints = list(state.previous_hints)
    expl = list(state.previous_explanations)
    mistakes = list(state.previous_mistakes)
    diagnoses = list(state.diagnoses)
    hint_index = state.hint_level_index
    encourage = state.encouragement_count

    if decision.hint_level is not None:
        hint_index = HINT_LADDER.index(decision.hint_level)
        if hint_text:
            if not hints or hints[-1] != hint_text:
                hints.append(hint_text)
            hints = hints[-MAX_HINT_HISTORY:]

    if decision.move.value in {"explain", "recap"} or (
        decision.hint_level in {HintLevel.full_explanation, HintLevel.worked_example}
    ):
        expl.append(utterance.strip()[:240])
        expl = expl[-MAX_EXPL_HISTORY:]

    diag = diagnosis or decision.diagnosis
    if diag is not None:
        mistakes.append(diag.kind.value)
        mistakes = mistakes[-MAX_MISTAKE_HISTORY:]
        diagnoses.append(diag)
        diagnoses = diagnoses[-MAX_MISTAKE_HISTORY:]

    if decision.include_motivation:
        encourage += 1

    return CoachingSessionState(
        student_id=state.student_id,
        language_id=state.language_id,
        session_id=state.session_id,
        grammar_id=state.grammar_id,
        activity_id=state.activity_id,
        hint_level_index=clamp_hint_index(hint_index),
        previous_hints=tuple(hints),
        previous_explanations=tuple(expl),
        previous_mistakes=tuple(mistakes),
        diagnoses=tuple(diagnoses),
        reflection_pending=bool(decision.include_reflection),
        last_move=decision.move.value,
        last_utterance_fingerprint=utterance_fingerprint(utterance),
        encouragement_count=encourage,
        schema_version=state.schema_version,
        updated_at=_now(),
    )


def state_to_dict(state: CoachingSessionState) -> dict:
    return {
        "student_id": state.student_id,
        "language_id": state.language_id,
        "session_id": state.session_id,
        "grammar_id": state.grammar_id,
        "activity_id": state.activity_id,
        "hint_level_index": state.hint_level_index,
        "previous_hints": list(state.previous_hints),
        "previous_explanations": list(state.previous_explanations),
        "previous_mistakes": list(state.previous_mistakes),
        "diagnoses": [
            {
                "kind": d.kind.value,
                "why": d.why,
                "evidence_notes": list(d.evidence_notes),
                "grammar_id": d.grammar_id,
            }
            for d in state.diagnoses
        ],
        "reflection_pending": state.reflection_pending,
        "last_move": state.last_move,
        "last_utterance_fingerprint": state.last_utterance_fingerprint,
        "encouragement_count": state.encouragement_count,
        "schema_version": state.schema_version,
        "updated_at": state.updated_at,
    }


def state_from_dict(raw: dict | None, *, student_id: int, language_id: int) -> CoachingSessionState | None:
    if not isinstance(raw, dict) or not raw:
        return None
    try:
        from app.services.language_ai_tutor_coaching.enums import MistakeKind
        from app.services.language_ai_tutor_coaching.types import MistakeDiagnosis

        diagnoses = tuple(
            MistakeDiagnosis(
                kind=MistakeKind(str(d.get("kind") or "unknown")),
                why=str(d.get("why") or ""),
                evidence_notes=tuple(str(x) for x in (d.get("evidence_notes") or [])),
                grammar_id=str(d.get("grammar_id") or ""),
            )
            for d in (raw.get("diagnoses") or [])
            if isinstance(d, dict)
        )
        return CoachingSessionState(
            student_id=int(raw.get("student_id") or student_id),
            language_id=int(raw.get("language_id") or language_id),
            session_id=str(raw.get("session_id") or new_session_id()),
            grammar_id=str(raw.get("grammar_id") or ""),
            activity_id=str(raw.get("activity_id") or ""),
            hint_level_index=clamp_hint_index(int(raw.get("hint_level_index") or 0)),
            previous_hints=tuple(str(x) for x in (raw.get("previous_hints") or [])),
            previous_explanations=tuple(str(x) for x in (raw.get("previous_explanations") or [])),
            previous_mistakes=tuple(str(x) for x in (raw.get("previous_mistakes") or [])),
            diagnoses=diagnoses,
            reflection_pending=bool(raw.get("reflection_pending")),
            last_move=str(raw.get("last_move") or ""),
            last_utterance_fingerprint=str(raw.get("last_utterance_fingerprint") or ""),
            encouragement_count=int(raw.get("encouragement_count") or 0),
            schema_version=int(raw.get("schema_version") or 1),
            updated_at=str(raw.get("updated_at") or ""),
        )
    except (TypeError, ValueError):
        return None
