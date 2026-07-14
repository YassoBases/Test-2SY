"""Infinite vocabulary generator — 100% offline (DB randomization + per-student de-duplication).

No LLM. `generate_batch` pulls N random catalog words matching the chosen topic/level that the learner
hasn't seen yet, records them as seen (so they never repeat), and returns them. When the section is
exhausted it reports "mastered". All inputs are parameter-bound (no SQL injection surface).
"""

from __future__ import annotations

import logging

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.language.vocabulary_catalog import (
    LanguageVocabularyCatalog,
    LanguageVocabularyCatalogSeen,
)

logger = logging.getLogger(__name__)

VALID_LEVELS = {"A1", "A2", "B1", "B2", "C1", "C2"}
MAX_BATCH = 20


def clean_level(level: str | None) -> str | None:
    """Normalize a CEFR level; return None if blank/invalid (so it isn't used as a filter)."""
    lvl = (level or "").strip().upper()
    return lvl if lvl in VALID_LEVELS else None


def clean_topic(topic: str | None) -> str | None:
    """Trim a topic; None when blank. (Used as a bound parameter, so injection-safe.)"""
    t = (topic or "").strip()
    return t[:60] if t else None


def _serialize(c: LanguageVocabularyCatalog) -> dict:
    return {
        "id": c.id,
        "word": c.word,
        "part_of_speech": c.part_of_speech,
        "translation": c.translation,
        "definition": c.definition,
        "context_theme": c.context_theme,
        "example_sentence": c.example_sentence,
        "cefr_level": c.cefr_level,
    }


async def get_options(db: AsyncSession) -> dict:
    """Distinct topics + levels present in the catalog (for the dropdowns)."""
    topics = [
        t for (t,) in (
            await db.execute(
                select(LanguageVocabularyCatalog.context_theme)
                .where(LanguageVocabularyCatalog.context_theme != "")
                .distinct()
                .order_by(LanguageVocabularyCatalog.context_theme)
            )
        ).all()
    ]
    levels = [
        lv for (lv,) in (
            await db.execute(
                select(LanguageVocabularyCatalog.cefr_level)
                .where(LanguageVocabularyCatalog.cefr_level != "")
                .distinct()
            )
        ).all()
    ]
    levels = [lv for lv in ("A1", "A2", "B1", "B2", "C1", "C2") if lv in set(levels)]
    return {"topics": topics, "levels": levels}


async def generate_batch(
    db: AsyncSession, *, student_id: int, topic: str | None = None, level: str | None = None, count: int = MAX_BATCH
) -> dict:
    """A fresh random batch of unseen words for the learner. Records them as seen (no repeats)."""
    count = max(1, min(int(count or MAX_BATCH), MAX_BATCH))
    topic = clean_topic(topic)
    level = clean_level(level)

    seen_subq = select(LanguageVocabularyCatalogSeen.catalog_id).where(
        LanguageVocabularyCatalogSeen.student_id == student_id
    )
    q = select(LanguageVocabularyCatalog).where(LanguageVocabularyCatalog.id.notin_(seen_subq))
    if topic:
        q = q.where(func.lower(LanguageVocabularyCatalog.context_theme) == topic.lower())
    if level:
        q = q.where(LanguageVocabularyCatalog.cefr_level == level)
    q = q.order_by(func.random()).limit(count)

    rows = (await db.execute(q)).scalars().all()
    if not rows:
        return {
            "words": [],
            "mastered": True,
            "message": "🎉 You've mastered every word in this section! Try another topic or level.",
        }

    # Mark these words as seen so this learner never gets them again.
    for r in rows:
        db.add(LanguageVocabularyCatalogSeen(student_id=student_id, catalog_id=r.id))
    await db.flush()

    return {"words": [_serialize(r) for r in rows], "mastered": False, "message": ""}
