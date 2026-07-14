from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.language.analytics import LanguageAnalytics
from app.models.language.assessment import LanguageAssessment, LanguageAssessmentSkillScore
from app.models.language.enums import (
    LanguageLevel,
    LanguageOnboardingStep,
    LanguagePlacementAttemptStatus,
    LanguageSkill,
)
from app.models.language.placement import (
    LanguagePlacementAttempt,
    LanguagePlacementQuestion,
    LanguagePlacementResponse,
    LanguagePlacementSection,
)
from app.models.language.profile import LanguageStudentProfile
from app.models.media import MediaObject, StorageProvider
from app.services.language_learning_path_service import generate_learning_path
from app.services.language_placement_scoring_service import (
    bottleneck_overall,
    percent_to_level,
    score_mcq,
    score_speaking,
    score_writing,
)
from app.services.language_placement_ai_scoring import score_speaking_ai, score_writing_ai
from app.services.language_validation import validate_speaking_duration, validate_writing_submission
from app.services.language_subscription_service import get_default_language
from app.services.media_storage_service import register_media_object

settings = get_settings()


async def _ensure_profile(db: AsyncSession, *, student_id: int, language_id: int) -> LanguageStudentProfile:
    result = await db.execute(
        select(LanguageStudentProfile).where(
            LanguageStudentProfile.student_id == student_id,
            LanguageStudentProfile.language_id == language_id,
        )
    )
    profile = result.scalar_one_or_none()
    if profile:
        return profile
    profile = LanguageStudentProfile(
        student_id=student_id,
        language_id=language_id,
        onboarding_step=LanguageOnboardingStep.placement,
        selected_at=datetime.now(timezone.utc),
    )
    db.add(profile)
    await db.flush()
    return profile


async def start_or_resume_attempt(db: AsyncSession, *, student_id: int) -> tuple[int, int]:
    language = await get_default_language(db)
    profile = await _ensure_profile(db, student_id=student_id, language_id=language.id)
    if profile.placement_completed_at:
        now = datetime.now(timezone.utc)
        allow_at = profile.next_allowed_retake_date
        if allow_at and allow_at.tzinfo is None:
            allow_at = allow_at.replace(tzinfo=timezone.utc)
        # Retake enforcement: block until next_allowed_retake_date (90 days after completion)
        if allow_at and allow_at > now:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "placement_retake_blocked",
                    "message": "You cannot retake the test now",
                    "next_allowed_retake_date": allow_at.isoformat(),
                },
            )
        # Past or missing allow_at: allow a retake attempt.

    existing = await db.execute(
        select(LanguagePlacementAttempt)
        .where(
            LanguagePlacementAttempt.student_id == student_id,
            LanguagePlacementAttempt.language_id == language.id,
            LanguagePlacementAttempt.status == LanguagePlacementAttemptStatus.in_progress,
        )
        .order_by(LanguagePlacementAttempt.started_at.desc())
        .limit(1)
    )
    attempt = existing.scalar_one_or_none()
    if attempt:
        return attempt.id, language.id

    attempt = LanguagePlacementAttempt(
        student_id=student_id,
        language_id=language.id,
        is_retake=bool(profile.placement_completed_at),
    )
    db.add(attempt)
    await db.flush()
    return attempt.id, language.id


async def get_bank_with_responses(
    db: AsyncSession, *, student_id: int, attempt_id: int
) -> tuple[list[LanguagePlacementSection], list[LanguagePlacementQuestion], dict[int, dict]]:
    attempt = await db.get(LanguagePlacementAttempt, attempt_id)
    if not attempt or attempt.student_id != student_id:
        raise HTTPException(status_code=404, detail="Attempt not found")

    sections_res = await db.execute(
        select(LanguagePlacementSection)
        .where(LanguagePlacementSection.language_id == attempt.language_id)
        .order_by(LanguagePlacementSection.sort_order)
    )
    sections = sections_res.scalars().all()
    qres = await db.execute(
        select(LanguagePlacementQuestion)
        .join(LanguagePlacementSection, LanguagePlacementSection.id == LanguagePlacementQuestion.section_id)
        .where(LanguagePlacementSection.language_id == attempt.language_id)
        .order_by(LanguagePlacementSection.sort_order, LanguagePlacementQuestion.sort_order, LanguagePlacementQuestion.id)
    )
    questions = qres.scalars().all()
    rres = await db.execute(
        select(LanguagePlacementResponse).where(LanguagePlacementResponse.attempt_id == attempt_id)
    )
    responses = rres.scalars().all()
    by_qid: dict[int, dict] = {}
    for r in responses:
        by_qid[int(r.question_id)] = r.response_json or {}
    return sections, questions, by_qid


async def save_response(
    db: AsyncSession,
    *,
    student_id: int,
    attempt_id: int,
    question_id: int,
    response_json: dict,
) -> None:
    attempt = await db.get(LanguagePlacementAttempt, attempt_id)
    if not attempt or attempt.student_id != student_id:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.status != LanguagePlacementAttemptStatus.in_progress:
        raise HTTPException(status_code=409, detail="This attempt is not in progress")

    question = await db.get(LanguagePlacementQuestion, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    existing = await db.execute(
        select(LanguagePlacementResponse).where(
            LanguagePlacementResponse.attempt_id == attempt_id,
            LanguagePlacementResponse.question_id == question_id,
        )
    )
    row = existing.scalar_one_or_none()
    if row:
        row.response_json = response_json
    else:
        db.add(
            LanguagePlacementResponse(
                attempt_id=attempt_id,
                question_id=question_id,
                response_json=response_json,
            )
        )
    await db.flush()


async def upload_speaking_audio(
    db: AsyncSession,
    *,
    student_id: int,
    attempt_id: int,
    question_id: int,
    file: UploadFile,
    duration_seconds: int | None = None,
) -> MediaObject:
    # Store to disk under student_* to reuse existing uploads mount.
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="The audio file is empty")
    ext = Path(file.filename or "speech.webm").suffix or ".webm"
    upload_dir = Path(settings.UPLOAD_DIR) / f"student_{student_id}" / "language_placement"
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / f"speaking_q{question_id}_{attempt_id}{ext}"
    dest.write_bytes(data)

    rel = dest.resolve().relative_to(Path(settings.UPLOAD_DIR).resolve())
    public_url = "/uploads/" + "/".join(rel.parts)
    storage_key = "/".join(rel.parts)

    media = await register_media_object(
        db,
        storage_path="uploads/" + storage_key,
        mime_type=file.content_type or "audio/webm",
        file_size_bytes=len(data),
        original_filename=file.filename or "speech.webm",
        uploaded_by_user_id=student_id,
        storage_provider=StorageProvider.local.value,
        storage_key=storage_key,
    )

    # Persist response_json with media_object_id (+ client-reported duration for scoring).
    response_json: dict = {"media_object_id": media.id}
    if duration_seconds is not None:
        response_json["duration_seconds"] = int(duration_seconds)
    await save_response(
        db,
        student_id=student_id,
        attempt_id=attempt_id,
        question_id=question_id,
        response_json=response_json,
    )
    # Caller can use media.public_url for immediate playback; we keep only the id in placement response.
    media.public_url = public_url
    return media


async def submit_attempt(db: AsyncSession, *, student_id: int, attempt_id: int) -> tuple[LanguageAssessment, int | None]:
    attempt = await db.get(LanguagePlacementAttempt, attempt_id)
    if not attempt or attempt.student_id != student_id:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.status != LanguagePlacementAttemptStatus.in_progress:
        raise HTTPException(status_code=409, detail="This attempt is not in progress")

    profile = await _ensure_profile(db, student_id=student_id, language_id=attempt.language_id)

    # Load questions/responses with section joins to determine skill.
    qres = await db.execute(
        select(LanguagePlacementQuestion, LanguagePlacementSection)
        .join(LanguagePlacementSection, LanguagePlacementSection.id == LanguagePlacementQuestion.section_id)
        .where(LanguagePlacementSection.language_id == attempt.language_id)
        .order_by(LanguagePlacementSection.sort_order, LanguagePlacementQuestion.sort_order, LanguagePlacementQuestion.id)
    )
    qrows = qres.all()
    rres = await db.execute(select(LanguagePlacementResponse).where(LanguagePlacementResponse.attempt_id == attempt_id))
    responses = {int(r.question_id): r for r in rres.scalars().all()}

    points_by_skill: dict[LanguageSkill, float] = {s: 0.0 for s in LanguageSkill}
    max_by_skill: dict[LanguageSkill, float] = {s: 0.0 for s in LanguageSkill}
    metrics_by_skill: dict[LanguageSkill, dict] = {s: {} for s in LanguageSkill}

    for q, sec in qrows:
        skill: LanguageSkill = sec.skill
        max_by_skill[skill] += float(q.max_points or 1)
        resp = responses.get(int(q.id))
        resp_json = resp.response_json if resp else {}

        if q.question_type in ("mcq", "mcq_listening"):
            pts = score_mcq(resp_json, q.answer_key_json, max_points=q.max_points or 1)
            points_by_skill[skill] += float(pts)
        elif q.question_type == "writing":
            min_words = int((q.prompt_json or {}).get("min_words") or 20)
            min_sentences = int((q.prompt_json or {}).get("min_sentences") or 0)
            text = str(resp_json.get("text") or resp_json.get("answer") or "").strip()
            if not text:
                # Skipped — score 0 like an MCQ skip; never block the whole submission.
                metrics_by_skill[skill].setdefault("writing_tasks", []).append({"skipped": True, "score_percent": 0})
            else:
                # Validate only a real (non-empty) response.
                validate_writing_submission(text, min_words=min_words, min_sentences=min_sentences)
                prompt_text = (q.prompt_json or {}).get("prompt") or (q.prompt_json or {}).get("instructions") or ""
                # Real CEFR grading of the content; fall back to length heuristic if AI is unavailable.
                ai_writing = await score_writing_ai(text=text, prompt=prompt_text)
                pct, m = ai_writing if ai_writing else score_writing(resp_json, min_words=min_words)
                points_by_skill[skill] += (pct / 100.0) * float(q.max_points or 10)
                metrics_by_skill[skill].setdefault("writing_tasks", []).append(m)
        elif q.question_type == "speaking":
            min_seconds = int((q.prompt_json or {}).get("min_seconds") or 20)
            if not resp_json.get("media_object_id"):
                # Skipped — score 0 like an MCQ skip; never block the whole submission.
                metrics_by_skill[skill].setdefault("speaking_tasks", []).append(
                    {"skipped": True, "has_media": False, "score_percent": 0}
                )
            else:
                raw_duration = resp_json.get("duration_seconds")
                if raw_duration is not None:
                    # Validate the minimum only when a real response with a duration is provided.
                    duration = validate_speaking_duration(raw_duration, min_seconds=min_seconds)
                    resp_json = {**resp_json, "duration_seconds": duration}
                # Real CEFR grading of the actual audio; fall back to duration heuristic if AI is unavailable.
                ai_speaking = None
                media = await db.get(MediaObject, int(resp_json["media_object_id"]))
                if media:
                    try:
                        audio_bytes = (Path(settings.UPLOAD_DIR) / media.storage_key).read_bytes()
                        ai_speaking = await score_speaking_ai(
                            audio_data=audio_bytes,
                            suffix=Path(media.storage_key).suffix or ".webm",
                            prompt=(q.prompt_json or {}).get("prompt") or "",
                        )
                    except Exception:
                        ai_speaking = None
                pct, m = ai_speaking if ai_speaking else score_speaking(resp_json, min_seconds=min_seconds)
                points_by_skill[skill] += (pct / 100.0) * float(q.max_points or 10)
                metrics_by_skill[skill].setdefault("speaking_tasks", []).append(m)

    # Create assessment + skill scores
    assessment = LanguageAssessment(
        student_id=student_id,
        language_id=attempt.language_id,
        attempt_id=attempt.id,
    )
    db.add(assessment)
    await db.flush()

    skill_levels: dict[LanguageSkill, LanguageLevel] = {}
    for skill in LanguageSkill:
        max_pts = max_by_skill.get(skill) or 0.0
        score_pct = round((points_by_skill.get(skill) or 0.0) / max_pts * 100.0, 2) if max_pts else 0.0
        level = percent_to_level(score_pct)
        skill_levels[skill] = level
        db.add(
            LanguageAssessmentSkillScore(
                assessment_id=assessment.id,
                skill=skill,
                score_percent=score_pct,
                level=level,
                raw_metrics_json=metrics_by_skill.get(skill) or None,
                ai_evaluation_json=None,
            )
        )

    overall = bottleneck_overall(skill_levels)
    assessment.overall_level = overall
    assessment.overall_calculation_method = "bottleneck"

    # Mark attempt/profile complete
    attempt.status = LanguagePlacementAttemptStatus.submitted
    attempt.submitted_at = datetime.now(timezone.utc)
    profile.placement_completed_at = datetime.now(timezone.utc)
    profile.last_assessment_date = profile.placement_completed_at
    profile.next_allowed_retake_date = profile.placement_completed_at + timedelta(days=90)
    profile.onboarding_step = LanguageOnboardingStep.dashboard

    # Update analytics for quick access payload
    analytics = await db.get(LanguageAnalytics, {"student_id": student_id, "language_id": attempt.language_id})
    if not analytics:
        analytics = LanguageAnalytics(student_id=student_id, language_id=attempt.language_id)
        db.add(analytics)
        await db.flush()
    analytics.reading_level = skill_levels[LanguageSkill.reading]
    analytics.listening_level = skill_levels[LanguageSkill.listening]
    analytics.writing_level = skill_levels[LanguageSkill.writing]
    analytics.speaking_level = skill_levels[LanguageSkill.speaking]
    analytics.overall_level_internal = overall

    from app.services.language_progression_service import sync_progression_from_skill_levels

    await sync_progression_from_skill_levels(
        db,
        student_id=student_id,
        language_id=attempt.language_id,
        skill_levels=skill_levels,
        overall=overall,
        source="placement",
    )

    # Generate weighted learning path
    path = await generate_learning_path(
        db,
        student_id=student_id,
        language_id=attempt.language_id,
        assessment_id=assessment.id,
        overall_level=overall,
        skill_levels=skill_levels,
    )
    await db.flush()

    return assessment, path.id

