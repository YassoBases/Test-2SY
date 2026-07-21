"""Development utilities — gated by DEBUG."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.deps import require_student_actor
from app.db.session import get_db
from app.models.user import User
from app.schemas.email import TestEmailRequest, TestEmailResponse
from app.schemas.language_dev_skip_placement import DevSkipPlacementIn, DevSkipPlacementOut
from app.services import email_service
from app.services.email_service import EmailDeliveryError
from app.services.language_access_service import build_language_access
from app.services.language_dev_skip_placement_service import skip_placement_from_scratch

router = APIRouter(prefix="/dev", tags=["Development"])


def _require_dev() -> None:
    # Read settings at call time (not import time) so DEBUG from .env is always current.
    if not get_settings().DEBUG:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


@router.post("/test-email", response_model=TestEmailResponse)
async def test_email(body: TestEmailRequest):
    """Send a branded test email via Resend (DEBUG mode only)."""
    _require_dev()
    if not email_service.is_email_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="أضف RESEND_API_KEY و EMAIL_FROM إلى البيئة",
        )
    try:
        result = await email_service.send_test_email(body.to)
    except EmailDeliveryError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"فشل إرسال البريد: {exc}",
        ) from exc

    message_id = result.get("id") if isinstance(result, dict) else None
    return TestEmailResponse(ok=True, message_id=message_id, detail="تم إرسال البريد بنجاح")


@router.post("/languages/skip-placement", response_model=DevSkipPlacementOut)
async def skip_language_placement(
    body: DevSkipPlacementIn | None = None,
    student: User = Depends(require_student_actor()),
    db: AsyncSession = Depends(get_db),
):
    """Developer shortcut: mark placement complete and start learning from a CEFR.

    Never available when DEBUG is false (404). Does not change placement scoring
    or curriculum engine algorithms — only reuses post-placement initialization.
    """
    _require_dev()
    payload = body or DevSkipPlacementIn()
    access = await build_language_access(db, student.id)
    if not access.subscribed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "language_subscription_required",
                "message": "Activate the language subscription before skipping placement",
                "redirect": "/student/languages/subscribe",
            },
        )

    try:
        result = await skip_placement_from_scratch(
            db,
            student_id=student.id,
            starting_cefr=payload.starting_cefr,
            bootstrap_learning=payload.bootstrap_learning,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    await db.commit()
    return DevSkipPlacementOut(**result)
