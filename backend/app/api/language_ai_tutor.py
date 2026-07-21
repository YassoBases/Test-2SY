"""Student AI Tutor Foundation API (Wave E1).

GET  /api/student/tutor/status
GET  /api/student/tutor/context
POST /api/student/tutor/turn
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_student_actor
from app.db.session import get_db
from app.models.user import User
from app.schemas.language_ai_tutor import (
    AiTutorContextOut,
    AiTutorStatusOut,
    AiTutorTurnIn,
    AiTutorTurnOut,
)
from app.services.language_access_service import require_language_learning_ready
from app.services.language_ai_tutor import (
    ai_tutor_enabled,
    build_tutor_context_async,
    respond_tutor_turn,
)
from app.services.language_ai_tutor.enums import TutorPromptKind
from app.services.language_ai_tutor.persona import resolve_teacher_persona
from app.services.language_ai_tutor.types import TutorTurnRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/student/tutor", tags=["Student AI Tutor"])


def _parse_kind(raw: str) -> TutorPromptKind:
    try:
        return TutorPromptKind(raw)
    except ValueError:
        return TutorPromptKind.answer_question


@router.get("/status", response_model=AiTutorStatusOut)
async def tutor_status(
    _student: User = Depends(require_student_actor()),
):
    return AiTutorStatusOut(enabled=ai_tutor_enabled())


@router.get("/context", response_model=AiTutorContextOut)
async def tutor_context(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
    grammar_id: str | None = None,
    lesson_id: str | None = None,
):
    if not ai_tutor_enabled():
        return AiTutorContextOut(enabled=False, student_id=student.id)

    req = TutorTurnRequest(
        student_id=student.id,
        grammar_id=grammar_id,
        lesson_id=lesson_id,
    )
    try:
        ctx = await build_tutor_context_async(db, req)
    except Exception:  # noqa: BLE001
        logger.exception("ai_tutor_context_failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Tutor context is temporarily unavailable.",
        ) from None

    return AiTutorContextOut(
        enabled=True,
        student_id=ctx.student_id,
        language_id=ctx.language_id,
        as_of=ctx.as_of,
        safety_code=ctx.safety_code.value,
        safety_message=ctx.safety_message,
        grammar_id=ctx.grammar.grammar_id if ctx.grammar else None,
        display_name=ctx.grammar.display_name if ctx.grammar else "",
        explanation_style=ctx.explanation_style.value,
        explainability_note=ctx.explainability_note,
        curriculum_version=ctx.curriculum_version,
        session=ctx.to_prompt_dict()["session"],
        teacher_persona=ctx.to_prompt_dict()["teacher_persona"],
        adaptive=ctx.to_prompt_dict()["adaptive"],
    )


@router.post("/turn", response_model=AiTutorTurnOut)
async def tutor_turn(
    body: AiTutorTurnIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    if not ai_tutor_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Tutor is disabled.",
        )

    persona = resolve_teacher_persona(persona_id=body.persona_id) if body.persona_id else None
    req = TutorTurnRequest(
        student_id=student.id,
        message=body.message,
        prompt_kind=_parse_kind(body.prompt_kind),
        conversation_id=body.conversation_id,
        grammar_id=body.grammar_id,
        lesson_id=body.lesson_id,
        activity_id=body.activity_id,
        step_id=body.step_id,
        student_language=body.student_language or "en",
        teacher_persona=persona,
    )
    try:
        result = await respond_tutor_turn(db, req)
    except Exception:  # noqa: BLE001
        logger.exception("ai_tutor_turn_failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Tutor is temporarily unavailable.",
        ) from None

    return AiTutorTurnOut(
        utterance=result.utterance,
        prompt_kind=result.prompt_kind.value,
        grammar_id=result.grammar_id,
        explanation_style=result.explanation_style.value,
        explainability_note=result.explainability_note,
        safety_code=result.safety_code.value,
        provider=result.provider,
        conversation_id=result.conversation_id,
        context_as_of=result.context_as_of,
        schema_version=result.schema_version,
    )
