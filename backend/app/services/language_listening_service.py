"""Adaptive, self-replenishing listening practice (mirrors the reading flow).

Serves one listening clip at a time at the student's current listening level (adaptive — the level
is nudged up/down by performance in submit_listening), generating fresh AI content on demand when the
bank runs low and synthesizing the audio for generated clips, so the supply is effectively infinite.
"""

from __future__ import annotations

import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.language.analytics import LanguageAnalytics
from app.models.language.content import LanguageContentItem
from app.models.language.enums import LanguageContentProgressStatus, LanguageLevel, LanguageSkill
from app.models.language.progress import LanguageListeningProgress
from app.services.language_content_service import lesson_body_for_student, resolve_listening_audio
from app.services.language_generation_gate import (
    can_generate,
    note_failure as note_generation_failure,
    note_success as note_generation_success,
)
from app.services.language_lesson_generation_service import generate_and_store
from app.services.language_subscription_service import get_default_language
from app.services.language_tts_service import get_lesson_audio

logger = logging.getLogger(__name__)

_ON_DEMAND_BATCH = 3


async def _adaptive_level(db: AsyncSession, *, student_id: int, language_id: int) -> str:
    analytics = await db.get(LanguageAnalytics, {"student_id": student_id, "language_id": language_id})
    if analytics and analytics.listening_level:
        return analytics.listening_level.value
    return "A2"


async def _unseen_listening(
    db: AsyncSession, *, student_id: int, language_id: int, level: str, generated_only: bool = False,
    newest: bool = False,
) -> LanguageContentItem | None:
    seen = select(LanguageListeningProgress.content_item_id).where(
        LanguageListeningProgress.student_id == student_id,
        LanguageListeningProgress.status == LanguageContentProgressStatus.completed,
    )
    q = select(LanguageContentItem).where(
        LanguageContentItem.language_id == language_id,
        LanguageContentItem.skill == LanguageSkill.listening,
        LanguageContentItem.content_type == "lesson",
        LanguageContentItem.level == LanguageLevel(level),
        LanguageContentItem.is_published.is_(True),
        LanguageContentItem.id.notin_(seen),
    )
    if generated_only:
        q = q.where(LanguageContentItem.body_json["source"].astext == "ai_nightly")
    # newest=True serves the just-generated clip (id desc); otherwise a random unseen one.
    q = q.order_by(LanguageContentItem.id.desc() if newest else func.random()).limit(1)
    return (await db.execute(q)).scalar_one_or_none()


async def _ensure_audio(db: AsyncSession, item: LanguageContentItem) -> tuple[str | None, bool]:
    """Existing clip URL, else synthesize from the transcript on demand (cached afterwards)."""
    audio_url, audio_available = await resolve_listening_audio(db, item)
    if audio_available:
        return audio_url, audio_available
    try:
        tts = await get_lesson_audio(db, content_item_id=item.id)
        await db.commit()  # the GET endpoint won't commit the cache row otherwise
        if tts and tts.get("public_url"):
            return tts["public_url"], True
    except Exception as exc:  # pragma: no cover - TTS variance
        logger.warning("Listening audio synthesis failed (%s): %s", item.id, exc)
    return None, False


async def next_listening(db: AsyncSession, *, student_id: int) -> dict | None:
    """The next adaptive listening clip (stripped of answers), generating content if the bank is low."""
    language = await get_default_language(db)
    level = await _adaptive_level(db, student_id=student_id, language_id=language.id)

    # Token-saving: serve an existing unseen AI clip first (free, instant). Generate ONLY when the
    # fresh-AI pool is exhausted, and skip while the breaker is tripped (e.g. Gemini credits depleted).
    item = await _unseen_listening(db, student_id=student_id, language_id=language.id, level=level, generated_only=True)
    if item is None and can_generate():
        from app.services.language_adaptive_generation_service import build_adaptive_context

        adaptive_context = await build_adaptive_context(
            db, student_id=student_id, language_id=language.id, skill="listening"
        )
        try:
            made = await generate_and_store(
                db, language_id=language.id, skill="listening", level=level, count=_ON_DEMAND_BATCH,
                adaptive_context=adaptive_context,
            )
            if made:
                note_generation_success()
                await db.commit()  # persist generated clips (GET endpoint won't commit otherwise)
                item = await _unseen_listening(
                    db, student_id=student_id, language_id=language.id, level=level,
                    generated_only=True, newest=True,
                )
            else:
                note_generation_failure()
        except Exception as exc:  # pragma: no cover - LLM variance
            logger.warning("On-demand listening generation failed (%s): %s", level, exc)
            note_generation_failure()
            await db.rollback()

    # Fallbacks: any unseen AI clip, then the seeded bank (always works offline).
    if item is None:
        item = await _unseen_listening(db, student_id=student_id, language_id=language.id, level=level)
    if item is None:
        return None

    audio_url, audio_available = await _ensure_audio(db, item)
    body = lesson_body_for_student(item)
    return {
        "id": item.id,
        "title": item.title,
        "level": item.level.value if item.level else level,
        "instructions": body.get("instructions") or "Listen and answer the questions.",
        "audio_url": audio_url,
        "audio_available": audio_available,
        "questions": body.get("questions") or [],
    }
