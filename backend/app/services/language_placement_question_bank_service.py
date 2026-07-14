"""Placement question-bank selection helpers.

This is the foundation for the smarter placement flow: reviewed bank items first,
boundary items when the engine is uncertain, and live AI generation only as a later fallback.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.language.enums import LanguageLevel
from app.models.language.question_bank import LanguagePlacementQuestionBankItem


PLACEMENT_BANK_SKILLS = frozenset(
    {
        "reading",
        "listening",
        "grammar_vocab",
        "writing_prompt",
        "speaking_prompt",
    }
)

_CEFR_ORDER = [
    LanguageLevel.A1,
    LanguageLevel.A2,
    LanguageLevel.B1,
    LanguageLevel.B2,
    LanguageLevel.C1,
    LanguageLevel.C2,
]


@dataclass(frozen=True)
class BoundaryTarget:
    low: LanguageLevel
    high: LanguageLevel


def normalize_bank_skill(skill: str) -> str:
    normalized = (skill or "").strip().lower().replace("-", "_")
    if normalized not in PLACEMENT_BANK_SKILLS:
        raise ValueError(f"Unsupported placement-bank skill: {skill!r}")
    return normalized


def normalize_level(level: LanguageLevel | str) -> LanguageLevel:
    if isinstance(level, LanguageLevel):
        return level
    return LanguageLevel(str(level).strip().upper())


def cefr_rank(level: LanguageLevel | str) -> int:
    normalized = normalize_level(level)
    return _CEFR_ORDER.index(normalized)


def boundary_between(a: LanguageLevel | str, b: LanguageLevel | str) -> BoundaryTarget | None:
    first = normalize_level(a)
    second = normalize_level(b)
    first_rank = cefr_rank(first)
    second_rank = cefr_rank(second)
    if abs(first_rank - second_rank) != 1:
        return None
    low, high = (first, second) if first_rank < second_rank else (second, first)
    return BoundaryTarget(low=low, high=high)


def adjacent_boundary(level: LanguageLevel | str, *, upward: bool) -> BoundaryTarget | None:
    rank = cefr_rank(level)
    neighbor_rank = rank + (1 if upward else -1)
    if neighbor_rank < 0 or neighbor_rank >= len(_CEFR_ORDER):
        return None
    return boundary_between(_CEFR_ORDER[rank], _CEFR_ORDER[neighbor_rank])


async def select_placement_bank_items(
    db: AsyncSession,
    *,
    language_id: int,
    skill: str,
    level: LanguageLevel | str,
    count: int = 2,
    used_item_ids: Iterable[int] | None = None,
    boundary: BoundaryTarget | tuple[LanguageLevel | str, LanguageLevel | str] | None = None,
    subskills: Sequence[str] | None = None,
    require_verified: bool = True,
) -> list[LanguagePlacementQuestionBankItem]:
    """Select reviewed placement items, preferring boundary items when requested.

    The function intentionally returns ORM rows instead of API schemas so the future exam
    flow can store internal fields like correct_index without exposing them to the frontend.
    """

    normalized_skill = normalize_bank_skill(skill)
    normalized_level = normalize_level(level)
    limit = max(1, int(count or 1))
    exclude_ids = {int(x) for x in (used_item_ids or []) if x is not None}
    wanted_subskills = [s for s in (subskills or []) if s]

    boundary_target: BoundaryTarget | None
    if isinstance(boundary, BoundaryTarget) or boundary is None:
        boundary_target = boundary
    else:
        boundary_target = boundary_between(boundary[0], boundary[1])

    async def _fetch(*, boundary_only: bool) -> list[LanguagePlacementQuestionBankItem]:
        stmt = (
            select(LanguagePlacementQuestionBankItem)
            .where(
                LanguagePlacementQuestionBankItem.language_id == language_id,
                LanguagePlacementQuestionBankItem.skill == normalized_skill,
                LanguagePlacementQuestionBankItem.is_active.is_(True),
            )
            .order_by(LanguagePlacementQuestionBankItem.usage_count.asc(), func.random())
            .limit(limit - len(selected))
        )
        if require_verified:
            stmt = stmt.where(LanguagePlacementQuestionBankItem.is_verified.is_(True))
        if exclude_ids:
            stmt = stmt.where(LanguagePlacementQuestionBankItem.id.not_in(exclude_ids))
        if wanted_subskills:
            stmt = stmt.where(LanguagePlacementQuestionBankItem.subskill.in_(wanted_subskills))

        if boundary_only and boundary_target:
            stmt = stmt.where(
                LanguagePlacementQuestionBankItem.boundary_low_level == boundary_target.low,
                LanguagePlacementQuestionBankItem.boundary_high_level == boundary_target.high,
            )
        else:
            stmt = stmt.where(LanguagePlacementQuestionBankItem.level == normalized_level)

        return list((await db.execute(stmt)).scalars().all())

    selected: list[LanguagePlacementQuestionBankItem] = []

    if boundary_target:
        for row in await _fetch(boundary_only=True):
            selected.append(row)
            exclude_ids.add(row.id)
            if len(selected) >= limit:
                return selected

    for row in await _fetch(boundary_only=False):
        selected.append(row)
        exclude_ids.add(row.id)
        if len(selected) >= limit:
            break

    return selected


def bank_item_to_exam_item(item: LanguagePlacementQuestionBankItem) -> dict:
    """Convert a bank item into the internal dict shape used by the placement exam state."""

    options = item.options_json if isinstance(item.options_json, list) else []
    body = item.body_json or {}
    content_item_id = body.get("content_item_id")
    try:
        content_item_id = int(content_item_id) if content_item_id is not None else None
    except (TypeError, ValueError):
        content_item_id = None
    return {
        "bank_item_id": item.id,
        "content_id": content_item_id,
        "audio_url": (item.audio_meta_json or {}).get("public_url"),
        "level": item.level.value,
        "boundary": (
            f"{item.boundary_low_level.value}/{item.boundary_high_level.value}"
            if item.boundary_low_level and item.boundary_high_level
            else ""
        ),
        "skill": item.skill,
        "subskill": item.subskill or "",
        "question_type": item.question_type,
        "passage": item.passage or "",
        "situation": item.situation or "",
        "question": item.prompt_text,
        "options": list(options),
        "correct_index": item.correct_index,
        "explanation": item.explanation or "",
        "media_object_id": item.media_object_id,
        "audio_meta": item.audio_meta_json or {},
        "body": body,
    }


async def record_bank_item_answer(db: AsyncSession, *, item_id: int, correct: bool) -> None:
    """Increment coarse calibration counters after a placement answer.

    The caller owns commit/rollback so this can be used inside a larger exam transaction.
    """

    values = {
        "usage_count": LanguagePlacementQuestionBankItem.usage_count + 1,
    }
    if correct:
        values["correct_count"] = LanguagePlacementQuestionBankItem.correct_count + 1

    await db.execute(
        update(LanguagePlacementQuestionBankItem)
        .where(LanguagePlacementQuestionBankItem.id == item_id)
        .values(**values)
    )
