"""Persist coaching session state under promotion_readiness_json['ai_tutor_coaching'].

Never mutates grammar.*, adaptive_intelligence, or ai_tutor (E1 memory) namespaces.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.services.language_ai_tutor_coaching.progression import state_from_dict, state_to_dict
from app.services.language_ai_tutor_coaching.types import (
    COACHING_JSONB_NAMESPACE,
    CoachingSessionState,
)
from app.services.language_grammar.ownership import (
    ADAPTIVE_JSONB_NAMESPACE_RESERVED,
    AI_TUTOR_JSONB_NAMESPACE_RESERVED,
    GRAMMAR_JSONB_NAMESPACE,
)
from app.services.language_progression_service import ensure_progression_row

SESSIONS_KEY = "sessions"
ACTIVE_SESSION_KEY = "active_session_id"


def coaching_bucket_from_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    return dict((payload or {}).get(COACHING_JSONB_NAMESPACE) or {})


def merge_coaching_into_payload(
    payload: dict[str, Any] | None,
    bucket: dict[str, Any],
) -> dict[str, Any]:
    out = dict(payload or {})
    for ns in (
        GRAMMAR_JSONB_NAMESPACE,
        ADAPTIVE_JSONB_NAMESPACE_RESERVED,
        AI_TUTOR_JSONB_NAMESPACE_RESERVED,
    ):
        if ns in out:
            out[ns] = dict(out[ns] or {})
    out[COACHING_JSONB_NAMESPACE] = dict(bucket)
    return out


async def load_coaching_state(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int = 1,
    session_id: str | None = None,
) -> CoachingSessionState | None:
    from sqlalchemy import select

    from app.models.language.progression import LanguageProgression

    result = await db.execute(
        select(LanguageProgression).where(
            LanguageProgression.student_id == student_id,
            LanguageProgression.language_id == language_id,
        )
    )
    row = result.scalar_one_or_none()
    if row is None:
        return None
    bucket = coaching_bucket_from_payload(dict(row.promotion_readiness_json or {}))
    sessions = dict(bucket.get(SESSIONS_KEY) or {})
    sid = session_id or bucket.get(ACTIVE_SESSION_KEY)
    if not sid or sid not in sessions:
        return None
    return state_from_dict(sessions[sid], student_id=student_id, language_id=language_id)


async def persist_coaching_state(
    db: AsyncSession,
    state: CoachingSessionState,
) -> CoachingSessionState:
    from sqlalchemy import select

    from app.models.language.progression import LanguageProgression

    await ensure_progression_row(
        db, student_id=state.student_id, language_id=state.language_id
    )
    result = await db.execute(
        select(LanguageProgression)
        .where(
            LanguageProgression.student_id == state.student_id,
            LanguageProgression.language_id == state.language_id,
        )
        .with_for_update()
    )
    row = result.scalar_one_or_none()
    if row is None:
        return state

    payload = dict(row.promotion_readiness_json or {})
    before = {
        GRAMMAR_JSONB_NAMESPACE: dict(payload.get(GRAMMAR_JSONB_NAMESPACE) or {}),
        ADAPTIVE_JSONB_NAMESPACE_RESERVED: dict(
            payload.get(ADAPTIVE_JSONB_NAMESPACE_RESERVED) or {}
        ),
        AI_TUTOR_JSONB_NAMESPACE_RESERVED: dict(
            payload.get(AI_TUTOR_JSONB_NAMESPACE_RESERVED) or {}
        ),
    }
    bucket = coaching_bucket_from_payload(payload)
    sessions = dict(bucket.get(SESSIONS_KEY) or {})
    sessions[state.session_id] = state_to_dict(state)
    if len(sessions) > 20:
        ordered = sorted(
            sessions.items(),
            key=lambda kv: str(kv[1].get("updated_at") or ""),
            reverse=True,
        )
        sessions = dict(ordered[:20])
    bucket[SESSIONS_KEY] = sessions
    bucket[ACTIVE_SESSION_KEY] = state.session_id
    merged = merge_coaching_into_payload(payload, bucket)
    for ns, snapshot in before.items():
        if dict(merged.get(ns) or {}) != snapshot:
            raise RuntimeError(f"Coaching persist refused: {ns} JSONB would change")

    row.promotion_readiness_json = merged
    flag_modified(row, "promotion_readiness_json")
    await db.flush()
    return state
