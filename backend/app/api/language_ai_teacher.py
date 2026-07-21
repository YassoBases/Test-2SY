"""Student Autonomous AI Teacher API (Phase F).

GET  /api/student/teacher/status
POST /api/student/teacher/session/start
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_student_actor
from app.db.session import get_db
from app.models.user import User
from app.schemas.language_ai_teacher import AiTeacherSessionOut, AiTeacherStatusOut
from app.services.language_access_service import require_language_learning_ready
from app.services.language_ai_teacher import ai_teacher_enabled, start_learning_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/student/teacher", tags=["Student AI Teacher"])


@router.get("/status", response_model=AiTeacherStatusOut)
async def teacher_status(
    _student: User = Depends(require_student_actor()),
):
    return AiTeacherStatusOut(enabled=ai_teacher_enabled())


@router.post("/session/start", response_model=AiTeacherSessionOut)
async def teacher_session_start(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
    session_length_minutes: int = 0,
    response_slow: bool = False,
):
    if not ai_teacher_enabled():
        return AiTeacherSessionOut(enabled=False, session={})

    try:
        session = await start_learning_session(
            db,
            student_id=student.id,
            session_length_minutes=session_length_minutes,
            response_slow=response_slow,
        )
    except Exception:  # noqa: BLE001
        logger.exception("ai_teacher_session_start_failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Teacher session is temporarily unavailable.",
        ) from None

    if session is None:
        return AiTeacherSessionOut(enabled=False, session={})

    return AiTeacherSessionOut(enabled=True, session=session.to_dict())
