"""Autonomous AI Teacher service — read locked layers; write ai_teacher sessions only."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.language_adaptive_intelligence import build_adaptive_bundle_async
from app.services.language_ai_teacher.flags import (
    ai_teacher_enabled,
    ai_teacher_persist_enabled,
)
from app.services.language_ai_teacher.orchestrator import orchestrate_learning_session
from app.services.language_ai_teacher.storage import persist_learning_session
from app.services.language_ai_teacher.types import LearningSession
from app.services.language_ai_tutor_coaching.storage import load_coaching_state
from app.services.language_grammar_mastery import get_grammar_mastery_snapshot
from app.services.language_grammar_progression import get_grammar_progression_snapshot


async def start_learning_session(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int = 1,
    as_of: str | None = None,
    session_length_minutes: int = 0,
    response_slow: bool = False,
    persist: bool | None = None,
) -> LearningSession | None:
    """Build today's AI Learning Session from Grammar + Adaptive + coaching signals."""
    if not ai_teacher_enabled():
        return None

    mastery = await get_grammar_mastery_snapshot(
        db, student_id=student_id, language_id=language_id
    )
    progression = await get_grammar_progression_snapshot(
        db, student_id=student_id, language_id=language_id
    )
    try:
        adaptive = await build_adaptive_bundle_async(
            db,
            student_id=student_id,
            language_id=language_id,
            as_of=as_of,
            persist_profile=False,
        )
    except Exception:  # noqa: BLE001
        from app.services.language_adaptive_intelligence import build_adaptive_bundle

        adaptive = build_adaptive_bundle(
            student_id=student_id,
            language_id=language_id,
            mastery=mastery,
            progression=progression,
            as_of=as_of,
            force_enabled=True,
        )

    coaching_mistakes = 0
    try:
        coaching = await load_coaching_state(
            db, student_id=student_id, language_id=language_id
        )
        if coaching is not None:
            coaching_mistakes = len(coaching.previous_mistakes)
    except Exception:  # noqa: BLE001
        coaching_mistakes = 0

    session = orchestrate_learning_session(
        student_id=student_id,
        language_id=language_id,
        mastery=mastery,
        progression=progression,
        adaptive=adaptive,
        coaching_mistake_count=coaching_mistakes,
        session_length_minutes=session_length_minutes,
        response_slow=response_slow,
        as_of=as_of,
    )

    do_persist = ai_teacher_persist_enabled() if persist is None else bool(persist)
    if do_persist:
        await persist_learning_session(db, session)
    return session


def build_learning_session_pure(
    *,
    student_id: int,
    language_id: int = 1,
    mastery=None,
    progression=None,
    adaptive=None,
    coaching_mistake_count: int = 0,
    session_length_minutes: int = 0,
    response_slow: bool = False,
    as_of: str | None = None,
    session_id: str | None = None,
) -> LearningSession:
    """Pure session assembly for verification / offline use."""
    return orchestrate_learning_session(
        student_id=student_id,
        language_id=language_id,
        mastery=mastery,
        progression=progression,
        adaptive=adaptive,
        coaching_mistake_count=coaching_mistake_count,
        session_length_minutes=session_length_minutes,
        response_slow=response_slow,
        as_of=as_of,
        session_id=session_id,
    )
