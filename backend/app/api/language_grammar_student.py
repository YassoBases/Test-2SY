"""Student Grammar Module API.



POST /api/student/grammar/lesson/start — generate-only lesson package.

POST /api/student/grammar/activity/complete — Wave B evidence→mastery→progression.

"""



from __future__ import annotations



import logging
import uuid



from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession



from app.core.config import get_settings
from app.db.session import get_db

from app.core.deps import require_student_actor

from app.models.user import User

from app.schemas.language_grammar_student import (

    GrammarActivityCompleteIn,

    GrammarActivityCompleteOut,

    GrammarDashboardOut,

    GrammarLessonOut,

    GrammarLessonStartIn,

    GrammarModuleStatusOut,
    GrammarPracticePreviewEvaluateIn,
    GrammarPracticePreviewEvaluateOut,

)

from app.services.language_access_service import require_language_learning_ready

from app.services.language_grammar_module import (

    build_grammar_dashboard,

    complete_grammar_activity,

    grammar_module_enabled,

    start_grammar_lesson,

)

from app.services.language_grammar_module.service import GrammarModuleError
from app.services.language_grammar_canonical_authoring.preview import (
    GrammarCanonicalPreviewError,
    build_canonical_revision_preview_lesson,
)
from app.services.language_grammar_canonical_authoring.practice_evaluation import (
    GrammarPracticeEvaluationError,
    evaluate_canonical_revision_preview_practice,
)



logger = logging.getLogger(__name__)



router = APIRouter(prefix="/student/grammar", tags=["Student Grammar"])





@router.get("/status", response_model=GrammarModuleStatusOut)

async def grammar_module_status(

    _student: User = Depends(require_student_actor()),

):

    return GrammarModuleStatusOut(enabled=grammar_module_enabled())





@router.get("/dashboard", response_model=GrammarDashboardOut)

async def grammar_dashboard(

    student: User = Depends(require_language_learning_ready()),

    db: AsyncSession = Depends(get_db),

):

    if not grammar_module_enabled():

        return GrammarDashboardOut(enabled=False)

    try:

        data = await build_grammar_dashboard(db, student_id=student.id)

        return GrammarDashboardOut(**data)

    except Exception:  # noqa: BLE001

        logger.exception("grammar_dashboard_failed")

        raise HTTPException(

            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,

            detail="Grammar is temporarily unavailable. Please try again.",

        ) from None





@router.post("/lesson/start", response_model=GrammarLessonOut)

async def grammar_lesson_start(

    body: GrammarLessonStartIn | None = None,

    student: User = Depends(require_language_learning_ready()),

    db: AsyncSession = Depends(get_db),

):

    if not grammar_module_enabled():

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Grammar module is not available.",

        )

    payload = body or GrammarLessonStartIn()

    try:

        lesson = await start_grammar_lesson(

            db,

            student_id=student.id,

            language_id=payload.language_id,

            use_llm_authoring=payload.use_llm_authoring,

        )

        return GrammarLessonOut(**lesson)

    except GrammarModuleError as exc:

        if exc.code == "module_disabled":

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grammar module is not available.") from None

        if exc.code == "no_grammar_target":

            raise HTTPException(

                status_code=status.HTTP_409_CONFLICT,

                detail="No grammar topic is ready yet. Complete language placement first.",

            ) from None

        logger.warning("grammar_lesson_start_failed code=%s", exc.code)

        raise HTTPException(

            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,

            detail="We couldn't generate your Grammar lesson. Please try again.",

        ) from None

    except Exception:  # noqa: BLE001

        logger.exception("grammar_lesson_start_unexpected")

        raise HTTPException(

            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,

            detail="We couldn't generate your Grammar lesson. Please try again.",

        ) from None





@router.get("/lesson/preview", response_model=GrammarLessonOut)
async def grammar_lesson_preview(
    revision_id: str,
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()
    if not settings.DEBUG or not settings.LANG_GRAMMAR_CANONICAL_PREVIEW_ENABLED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grammar lesson preview is not available.")

    try:
        parsed_revision_id = uuid.UUID(str(revision_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid revision_id.") from None

    try:
        lesson = await build_canonical_revision_preview_lesson(db, revision_id=parsed_revision_id)
        return GrammarLessonOut(**lesson)
    except GrammarCanonicalPreviewError as exc:
        if exc.code in {"revision_not_found", "canonical_lesson_not_found"}:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grammar lesson preview was not found.") from None
        if exc.code == "revision_not_reviewable":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This Grammar lesson revision is not ready for review.",
            ) from None
        logger.warning("grammar_lesson_preview_failed code=%s", exc.code)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This Grammar lesson revision cannot be previewed safely.",
        ) from None
    except Exception:  # noqa: BLE001
        logger.exception("grammar_lesson_preview_unexpected")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Grammar lesson preview is temporarily unavailable.",
        ) from None


@router.post("/lesson/preview/practice/evaluate", response_model=GrammarPracticePreviewEvaluateOut)
async def grammar_lesson_preview_practice_evaluate(
    body: GrammarPracticePreviewEvaluateIn,
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()
    if not settings.DEBUG or not settings.LANG_GRAMMAR_CANONICAL_PREVIEW_ENABLED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grammar lesson preview is not available.")

    try:
        parsed_revision_id = uuid.UUID(str(body.revision_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid revision_id.") from None

    try:
        result = await evaluate_canonical_revision_preview_practice(
            db,
            revision_id=parsed_revision_id,
            item_id=body.item_id,
            learner_response=body.learner_response,
            attempt_number=body.attempt_number,
        )
        return GrammarPracticePreviewEvaluateOut(**result.to_dict())
    except GrammarPracticeEvaluationError as exc:
        if exc.code in {"revision_not_found", "canonical_lesson_not_found", "unknown_task_id"}:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Practice item was not found.") from None
        if exc.code == "revision_not_reviewable":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This Grammar lesson revision is not ready for practice preview.",
            ) from None
        logger.warning("grammar_lesson_preview_practice_evaluate_failed code=%s", exc.code)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This practice item cannot be evaluated safely.",
        ) from None
    except Exception:  # noqa: BLE001
        logger.exception("grammar_lesson_preview_practice_evaluate_unexpected")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Practice evaluation is temporarily unavailable.",
        ) from None


@router.post("/activity/complete", response_model=GrammarActivityCompleteOut)

async def grammar_activity_complete(

    body: GrammarActivityCompleteIn,

    student: User = Depends(require_language_learning_ready()),

    db: AsyncSession = Depends(get_db),

):

    """Wave D — attested completion; client may not send grammar_id or score."""

    if not grammar_module_enabled():

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="Grammar module is not available.",

        )

    try:

        result = await complete_grammar_activity(

            db,

            student_id=student.id,

            language_id=body.language_id,

            activity_session_id=body.activity_session_id,

            answers=body.answers,

            response_text=body.response_text,

        )

        return GrammarActivityCompleteOut(**result)

    except GrammarModuleError as exc:

        if exc.code == "module_disabled":

            raise HTTPException(

                status_code=status.HTTP_404_NOT_FOUND,

                detail="Grammar module is not available.",

            ) from None

        if exc.code in {
            "invalid_skill",
            "invalid_evidence",
            "invalid_student",
            "stamp_forged",
            "student_ownership",
            "session_not_found",
            "session_not_open",
            "session_expired",
            "duplicate_observation",
            "invalid_session_id",
            "score_unavailable",
            "stamp_student_mismatch",
            "stamp_grammar_mismatch",
            "stamp_session_mismatch",
        }:

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from None

        logger.warning("grammar_activity_complete_failed code=%s", exc.code)

        raise HTTPException(

            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,

            detail="We couldn't record your Grammar progress. Please try again.",

        ) from None

    except Exception:  # noqa: BLE001

        logger.exception("grammar_activity_complete_unexpected")

        raise HTTPException(

            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,

            detail="We couldn't record your Grammar progress. Please try again.",

        ) from None

