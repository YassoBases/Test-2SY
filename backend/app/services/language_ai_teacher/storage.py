"""Persist generated AI Teacher sessions under promotion_readiness_json['ai_teacher'].

Never mutates grammar / adaptive / ai_tutor / ai_tutor_coaching educational or tutor state.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.services.language_ai_teacher.types import AI_TEACHER_JSONB_NAMESPACE, LearningSession
from app.services.language_grammar.ownership import (
    ADAPTIVE_JSONB_NAMESPACE_RESERVED,
    AI_TUTOR_COACHING_JSONB_NAMESPACE_RESERVED,
    AI_TUTOR_JSONB_NAMESPACE_RESERVED,
    GRAMMAR_JSONB_NAMESPACE,
)
from app.services.language_progression_service import ensure_progression_row

SESSIONS_KEY = "sessions"
ACTIVE_SESSION_KEY = "active_session_id"
PROTECTED_NAMESPACES = (
    GRAMMAR_JSONB_NAMESPACE,
    ADAPTIVE_JSONB_NAMESPACE_RESERVED,
    AI_TUTOR_JSONB_NAMESPACE_RESERVED,
    AI_TUTOR_COACHING_JSONB_NAMESPACE_RESERVED,
)


def teacher_bucket_from_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    return dict((payload or {}).get(AI_TEACHER_JSONB_NAMESPACE) or {})


def merge_teacher_into_payload(
    payload: dict[str, Any] | None,
    bucket: dict[str, Any],
) -> dict[str, Any]:
    out = dict(payload or {})
    for ns in PROTECTED_NAMESPACES:
        if ns in out:
            out[ns] = dict(out[ns] or {})
    out[AI_TEACHER_JSONB_NAMESPACE] = dict(bucket)
    return out


async def persist_learning_session(
    db: AsyncSession,
    session: LearningSession,
) -> LearningSession:
    from sqlalchemy import select

    from app.models.language.progression import LanguageProgression

    await ensure_progression_row(
        db, student_id=session.student_id, language_id=session.language_id
    )
    result = await db.execute(
        select(LanguageProgression)
        .where(
            LanguageProgression.student_id == session.student_id,
            LanguageProgression.language_id == session.language_id,
        )
        .with_for_update()
    )
    row = result.scalar_one_or_none()
    if row is None:
        return session

    payload = dict(row.promotion_readiness_json or {})
    before = {ns: dict(payload.get(ns) or {}) for ns in PROTECTED_NAMESPACES}
    bucket = teacher_bucket_from_payload(payload)
    sessions = dict(bucket.get(SESSIONS_KEY) or {})
    sessions[session.session_id] = session.to_dict()
    if len(sessions) > 30:
        ordered = sorted(
            sessions.items(),
            key=lambda kv: str((kv[1] or {}).get("as_of") or ""),
            reverse=True,
        )
        sessions = dict(ordered[:30])
    bucket[SESSIONS_KEY] = sessions
    bucket[ACTIVE_SESSION_KEY] = session.session_id
    merged = merge_teacher_into_payload(payload, bucket)
    for ns, snapshot in before.items():
        if dict(merged.get(ns) or {}) != snapshot:
            raise RuntimeError(f"AI Teacher persist refused: {ns} JSONB would change")

    row.promotion_readiness_json = merged
    flag_modified(row, "promotion_readiness_json")
    await db.flush()
    return session
