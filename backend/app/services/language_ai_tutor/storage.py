"""Persist conversation memory under promotion_readiness_json['ai_tutor'].

Never reads or writes grammar.* / adaptive_intelligence educational keys for mutation.
Adaptive namespace may be read elsewhere; this module only touches ai_tutor.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.services.language_ai_tutor.memory import memory_from_dict, memory_to_dict
from app.services.language_ai_tutor.types import AI_TUTOR_JSONB_NAMESPACE, ConversationMemory
from app.services.language_grammar.ownership import (
    ADAPTIVE_JSONB_NAMESPACE_RESERVED,
    GRAMMAR_JSONB_NAMESPACE,
)
from app.services.language_progression_service import ensure_progression_row

MEMORY_BUCKET_KEY = "conversation_memory"
ACTIVE_CONVERSATION_KEY = "active_conversation_id"


def tutor_bucket_from_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    return dict((payload or {}).get(AI_TUTOR_JSONB_NAMESPACE) or {})


def merge_tutor_into_payload(
    payload: dict[str, Any] | None,
    bucket: dict[str, Any],
) -> dict[str, Any]:
    out = dict(payload or {})
    if GRAMMAR_JSONB_NAMESPACE in out:
        out[GRAMMAR_JSONB_NAMESPACE] = dict(out[GRAMMAR_JSONB_NAMESPACE] or {})
    if ADAPTIVE_JSONB_NAMESPACE_RESERVED in out:
        out[ADAPTIVE_JSONB_NAMESPACE_RESERVED] = dict(
            out[ADAPTIVE_JSONB_NAMESPACE_RESERVED] or {}
        )
    out[AI_TUTOR_JSONB_NAMESPACE] = dict(bucket)
    return out


def conversations_from_bucket(bucket: dict[str, Any]) -> dict[str, dict]:
    raw = bucket.get("conversations") or {}
    if not isinstance(raw, dict):
        return {}
    return {str(k): dict(v) for k, v in raw.items() if isinstance(v, dict)}


async def load_conversation_memory(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int = 1,
    conversation_id: str | None = None,
) -> ConversationMemory | None:
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
    bucket = tutor_bucket_from_payload(dict(row.promotion_readiness_json or {}))
    convos = conversations_from_bucket(bucket)
    cid = conversation_id or bucket.get(ACTIVE_CONVERSATION_KEY)
    if not cid or cid not in convos:
        return None
    return memory_from_dict(convos[cid], student_id=student_id, language_id=language_id)


async def persist_conversation_memory(
    db: AsyncSession,
    memory: ConversationMemory,
) -> ConversationMemory:
    from app.services.language_grammar_progression.locking import lock_grammar_progression_row

    await ensure_progression_row(
        db, student_id=memory.student_id, language_id=memory.language_id
    )
    row = await lock_grammar_progression_row(
        db, student_id=memory.student_id, language_id=memory.language_id
    )
    if row is None:
        return memory

    payload = dict(row.promotion_readiness_json or {})
    grammar_before = dict(payload.get(GRAMMAR_JSONB_NAMESPACE) or {})
    adaptive_before = dict(payload.get(ADAPTIVE_JSONB_NAMESPACE_RESERVED) or {})
    bucket = tutor_bucket_from_payload(payload)
    convos = conversations_from_bucket(bucket)
    convos[memory.conversation_id] = memory_to_dict(memory)
    # Cap stored conversations
    if len(convos) > 20:
        ordered = sorted(
            convos.items(),
            key=lambda kv: str(kv[1].get("updated_at") or ""),
            reverse=True,
        )
        convos = dict(ordered[:20])
    bucket["conversations"] = convos
    bucket[ACTIVE_CONVERSATION_KEY] = memory.conversation_id
    merged = merge_tutor_into_payload(payload, bucket)
    if dict(merged.get(GRAMMAR_JSONB_NAMESPACE) or {}) != grammar_before:
        raise RuntimeError("AI Tutor persist refused: grammar JSONB would change")
    if dict(merged.get(ADAPTIVE_JSONB_NAMESPACE_RESERVED) or {}) != adaptive_before:
        raise RuntimeError("AI Tutor persist refused: adaptive JSONB would change")

    row.promotion_readiness_json = merged
    flag_modified(row, "promotion_readiness_json")
    await db.flush()
    return memory
