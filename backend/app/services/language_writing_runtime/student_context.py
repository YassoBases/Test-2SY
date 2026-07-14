"""Student context helpers for writing runtime (W6) — read official level only."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.language.progression import LanguageProgression
from app.services.language_writing.enums import OfficialWritingCEFR
from app.services.language_writing_curriculum.goal_resolver import resolve_goal_from_metadata
from app.services.language_writing.enums import WritingGoal


async def official_writing_cefr_for_student(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int,
    default: OfficialWritingCEFR = OfficialWritingCEFR.B1,
) -> OfficialWritingCEFR:
    result = await db.execute(
        select(LanguageProgression).where(
            LanguageProgression.student_id == student_id,
            LanguageProgression.language_id == language_id,
        )
    )
    row = result.scalar_one_or_none()
    if row is None:
        return default
    try:
        return OfficialWritingCEFR(row.official_writing_cefr.value)
    except ValueError:
        return default


def writing_goal_from_preferences(preferences: dict[str, object] | None) -> WritingGoal:
    return resolve_goal_from_metadata(preferences)
