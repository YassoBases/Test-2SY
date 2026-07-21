"""Persist adaptive profile under promotion_readiness_json['adaptive_intelligence'].

Never reads or writes grammar.* mastery / progression / review keys.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.services.language_adaptive_intelligence.profile import profile_from_dict, profile_to_dict
from app.services.language_adaptive_intelligence.types import (
    ADAPTIVE_JSONB_NAMESPACE,
    StudentLearningProfile,
)
from app.services.language_grammar.ownership import GRAMMAR_JSONB_NAMESPACE
from app.services.language_progression_service import ensure_progression_row


PROFILE_BUCKET_KEY = "learning_profile"


def adaptive_bucket_from_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    return dict((payload or {}).get(ADAPTIVE_JSONB_NAMESPACE) or {})


def merge_adaptive_into_payload(
    payload: dict[str, Any] | None,
    bucket: dict[str, Any],
) -> dict[str, Any]:
    """Merge adaptive namespace only — grammar root is preserved untouched."""
    out = dict(payload or {})
    # Preserve grammar namespace byte-for-byte reference copy
    if GRAMMAR_JSONB_NAMESPACE in out:
        out[GRAMMAR_JSONB_NAMESPACE] = dict(out[GRAMMAR_JSONB_NAMESPACE] or {})
    out[ADAPTIVE_JSONB_NAMESPACE] = dict(bucket)
    return out


def load_profile_from_payload(
    payload: dict[str, Any] | None,
    *,
    student_id: int,
    language_id: int,
) -> StudentLearningProfile | None:
    bucket = adaptive_bucket_from_payload(payload)
    return profile_from_dict(
        bucket.get(PROFILE_BUCKET_KEY),
        student_id=student_id,
        language_id=language_id,
    )


async def load_learning_profile(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int = 1,
) -> StudentLearningProfile | None:
    """Read-only profile load — no row lock."""
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
    return load_profile_from_payload(
        dict(row.promotion_readiness_json or {}),
        student_id=student_id,
        language_id=language_id,
    )


async def persist_learning_profile(
    db: AsyncSession,
    profile: StudentLearningProfile,
) -> StudentLearningProfile:
    """Persist adaptive profile only — never mutates grammar JSONB subtree."""
    from app.services.language_grammar_progression.locking import lock_grammar_progression_row

    await ensure_progression_row(
        db, student_id=profile.student_id, language_id=profile.language_id
    )
    row = await lock_grammar_progression_row(
        db, student_id=profile.student_id, language_id=profile.language_id
    )
    if row is None:
        return profile

    payload = dict(row.promotion_readiness_json or {})
    grammar_before = dict(payload.get(GRAMMAR_JSONB_NAMESPACE) or {})
    bucket = adaptive_bucket_from_payload(payload)
    bucket[PROFILE_BUCKET_KEY] = profile_to_dict(profile)
    merged = merge_adaptive_into_payload(payload, bucket)
    grammar_after = dict(merged.get(GRAMMAR_JSONB_NAMESPACE) or {})
    if grammar_before != grammar_after:
        raise RuntimeError("Adaptive persist refused: grammar JSONB would change")

    row.promotion_readiness_json = merged
    flag_modified(row, "promotion_readiness_json")
    await db.flush()
    return profile
