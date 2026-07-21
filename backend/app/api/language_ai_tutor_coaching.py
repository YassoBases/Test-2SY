"""Student Conversational Coaching API (Wave E2).

GET  /api/student/tutor/coach/status
POST /api/student/tutor/coach/turn
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_student_actor
from app.db.session import get_db
from app.models.user import User
from app.schemas.language_ai_tutor_coaching import (
    CoachingStatusOut,
    CoachingTurnIn,
    CoachingTurnOut,
    CoachingWrapUpOut,
)
from app.services.language_access_service import require_language_learning_ready
from app.services.language_ai_tutor_coaching import (
    CoachingTurnRequest,
    conversational_coaching_enabled,
    respond_coaching_turn,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/student/tutor/coach", tags=["Student AI Tutor Coaching"])


@router.get("/status", response_model=CoachingStatusOut)
async def coaching_status(
    _student: User = Depends(require_student_actor()),
):
    return CoachingStatusOut(enabled=conversational_coaching_enabled())


@router.post("/turn", response_model=CoachingTurnOut)
async def coaching_turn(
    body: CoachingTurnIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    if not conversational_coaching_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Conversational coaching is disabled.",
        )

    req = CoachingTurnRequest(
        student_id=student.id,
        message=body.message,
        session_id=body.session_id,
        conversation_id=body.conversation_id,
        grammar_id=body.grammar_id,
        lesson_id=body.lesson_id,
        activity_id=body.activity_id,
        step_id=body.step_id,
        student_attempt=body.student_attempt,
        is_correct=body.is_correct,
        request_full_answer=body.request_full_answer,
        request_wrap_up=body.request_wrap_up,
        student_language=body.student_language or "en",
    )
    try:
        result = await respond_coaching_turn(db, req)
    except Exception:  # noqa: BLE001
        logger.exception("coaching_turn_failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Conversational coaching is temporarily unavailable.",
        ) from None

    wrap = None
    if result.wrap_up is not None:
        wrap = CoachingWrapUpOut(
            todays_grammar=result.wrap_up.todays_grammar,
            grammar_id=result.wrap_up.grammar_id,
            common_mistakes=list(result.wrap_up.common_mistakes),
            strong_performance=list(result.wrap_up.strong_performance),
            suggested_review=result.wrap_up.suggested_review,
            next_lesson_preview=result.wrap_up.next_lesson_preview,
            summary_text=result.wrap_up.summary_text,
        )

    return CoachingTurnOut(
        utterance=result.utterance,
        move=result.move.value,
        hint_level=result.hint_level,
        explanation_variety=result.explanation_variety,
        diagnosis_kind=result.diagnosis_kind,
        diagnosis_why=result.diagnosis_why,
        reflection_question=result.reflection_question,
        motivation_line=result.motivation_line,
        explainability_note=result.explainability_note,
        reasons=list(result.reasons),
        session_id=result.session_id,
        grammar_id=result.grammar_id,
        provider=result.provider,
        wrap_up=wrap,
        safety_code=result.safety_code,
        schema_version=result.schema_version,
    )
