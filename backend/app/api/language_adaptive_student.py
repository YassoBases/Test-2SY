"""Student Adaptive Learning Intelligence API (Phase 2).

GET /api/student/adaptive/status
GET /api/student/adaptive/insights
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_student_actor
from app.db.session import get_db
from app.models.user import User
from app.schemas.language_adaptive_student import (
    AdaptiveDifficultyOut,
    AdaptiveInsightsOut,
    AdaptiveParentOut,
    AdaptiveProfileOut,
    AdaptiveRemediationOut,
    AdaptiveReviewOut,
    AdaptiveSignalOut,
    AdaptiveStatusOut,
    AdaptiveTeacherOut,
)
from app.services.language_access_service import require_language_learning_ready
from app.services.language_adaptive_intelligence import (
    adaptive_intelligence_enabled,
    build_adaptive_bundle_async,
)
from app.services.language_adaptive_intelligence.parent import parent_insight_to_dict
from app.services.language_adaptive_intelligence.teacher import teacher_insight_to_dict

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/student/adaptive", tags=["Student Adaptive"])


@router.get("/status", response_model=AdaptiveStatusOut)
async def adaptive_status(
    _student: User = Depends(require_student_actor()),
):
    return AdaptiveStatusOut(enabled=adaptive_intelligence_enabled())


@router.get("/insights", response_model=AdaptiveInsightsOut)
async def adaptive_insights(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    if not adaptive_intelligence_enabled():
        return AdaptiveInsightsOut(enabled=False, student_id=student.id)

    try:
        bundle = await build_adaptive_bundle_async(db, student_id=student.id)
    except Exception:  # noqa: BLE001
        logger.exception("adaptive_insights_failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Adaptive insights are temporarily unavailable. Please try again.",
        ) from None

    student_dict = bundle.to_student_dict()
    teacher = teacher_insight_to_dict(bundle.teacher)
    parent = parent_insight_to_dict(bundle.parent)
    difficulty = None
    if student_dict.get("difficulty"):
        difficulty = AdaptiveDifficultyOut(**student_dict["difficulty"])

    return AdaptiveInsightsOut(
        enabled=bundle.enabled,
        student_id=bundle.student_id,
        language_id=bundle.language_id,
        as_of=bundle.as_of,
        current_grammar_id=bundle.current_grammar_id,
        profile=AdaptiveProfileOut(**student_dict["profile"]),
        difficulty=difficulty,
        review_recommendations=[
            AdaptiveReviewOut(**row) for row in student_dict["review_recommendations"]
        ],
        activity_mix=student_dict["activity_mix"],
        activity_mix_reasons=student_dict["activity_mix_reasons"],
        remediations=[AdaptiveRemediationOut(**row) for row in student_dict["remediations"]],
        signals=[AdaptiveSignalOut(**row) for row in student_dict["signals"]],
        teacher=AdaptiveTeacherOut(**teacher),
        parent=AdaptiveParentOut(**parent),
        schema_version=bundle.schema_version,
    )
