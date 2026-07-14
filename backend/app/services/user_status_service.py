"""Compute onboarding / setup flags for auth responses."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import TeacherProfile
from app.models.enrollment import OnboardingStep
from app.models.profile import StudentProfile
from app.models.user import User, UserRole


async def get_student_profile(db: AsyncSession, user_id: int) -> StudentProfile:
    result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        try:
            profile = StudentProfile(
                user_id=user_id,
                interests_json="[]",
                difficulty="medium",
                onboarding_step=OnboardingStep.grade,
            )
            db.add(profile)
            await db.flush()
        except Exception:
            await db.rollback()
            result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == user_id))
            profile = result.scalar_one_or_none()
    return profile


async def student_flags(db: AsyncSession, user_id: int) -> dict:
    profile = await get_student_profile(db, user_id)
    return {
        "onboarding_complete": True,
        "needs_payment": False,
        "payment_complete": True,
        "teacher_setup_complete": True,
        "onboarding_step": "complete",
        "grade": profile.grade,
    }


async def teacher_setup_complete(db: AsyncSession, user_id: int) -> bool:
    result = await db.execute(select(TeacherProfile).where(TeacherProfile.user_id == user_id))
    tp = result.scalar_one_or_none()
    return bool(tp and tp.setup_completed_at)


async def build_user_extras(db: AsyncSession, user: User) -> dict:
    if user.role == UserRole.student:
        return await student_flags(db, user.id)
    if user.role == UserRole.teacher:
        complete = await teacher_setup_complete(db, user.id)
        return {
            "onboarding_complete": True,
            "needs_payment": False,
            "payment_complete": True,
            "teacher_setup_complete": complete,
            "onboarding_step": "complete",
            "grade": None,
        }
    return {
        "onboarding_complete": True,
        "needs_payment": False,
        "payment_complete": True,
        "teacher_setup_complete": True,
        "onboarding_step": "complete",
        "grade": None,
    }
