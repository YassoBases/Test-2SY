"""Student Language Learning — access, placement, and Phase C1 lessons."""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_student_actor
from app.core.listening_deployment_deps import require_listening_deployment_ready
from app.db.session import get_db
from app.models.language.analytics import LanguageAnalytics
from app.models.language.assessment import LanguageAssessmentSkillScore
from app.models.language.enums import LanguageLevel, LanguageSkill
from app.models.language.placement import LanguagePlacementAttempt
from app.models.user import User
from app.schemas.language import LanguageAccessOut, LanguageProductOut, LanguageSubscribeOut, LanguageSubscribeRequest
from app.schemas.language_listening_acquisition import ListeningNextResponseOut
from app.schemas.language_listening_bundles import (
    LessonExperienceBundleOut,
    ListeningJourneyBundleOut,
    ListeningLessonSubmitBundleOut,
)
from app.schemas.language_learning import (
    LanguageHubOut,
    LanguageProgressOut,
    LessonListItemOut,
    LessonListOut,
    LessonProgressOut,
    LessonSubmitIn,
    LessonSubmitOut,
    ListeningLessonOut,
    ReadingLessonOut,
    DictionarySearchOut,
    VocabularyCardOut,
    LearnerModelProfileOut,
    LearnerPracticeSetOut,
    LearnerPracticeSubmitIn,
    LearnerPracticeSubmitOut,
    ReadingAudioOut,
    ReadingExplainIn,
    ReadingExplainOut,
    ReadingHistoryItemOut,
    ReadingInsightsOut,
    ReadingSummaryIn,
    ReadingSummaryOut,
    ReadingTopicsIn,
    ReadingTopicsOut,
    LearnerMemoryOut,
    LearnerMemoryUpdateIn,
    VocabularyChallengeOut,
    VocabularyChallengeSubmitIn,
    VocabularyChallengeSubmitOut,
    VocabularySaveIn,
    VocabularySaveOut,
    VocabularyListOut,
    VocabularyReviewIn,
    WordAnalysisIn,
    WordAnalysisOut,
    WritingListOut,
    WritingPromptOut,
    WritingSubmitIn,
    WritingSubmitOut,
)
from app.schemas.language_placement import (
    PlacementResultsOut,
    PlacementSaveResponseIn,
    PlacementSaveResponseOut,
    PlacementSpeakingUploadOut,
    PlacementStartOut,
    PlacementSubmitIn,
)
from app.schemas.language_writing_bundles import (
    WritingDraftSubmitIn,
    WritingDraftSubmitOut,
    WritingGenerateIn,
    WritingGenerateOut,
    WritingJourneyBundleOut,
)
from app.services.language_access_service import (
    build_language_access,
    require_active_language_subscription,
    require_language_learning_ready,
)
from app.services.language_content_service import (
    get_listening_lesson,
    get_reading_lesson,
    lesson_body_for_student,
    list_lessons,
    resolve_listening_audio,
)
from app.services.language_curriculum_service import build_curriculum_overview, record_objective_practice
from app.services.language_microlesson_service import get_micro_lesson
from app.services.language_xp_service import award_daily_mission_xp, get_xp_overview
from app.services.language_daily_plan_service import build_daily_plan
from app.services.language_daily_mission_service import build_daily_mission, renew_daily_mission
from app.services.language_subscription_service import get_default_language
from app.services.language_hub_service import build_language_hub, build_language_progress
from app.schemas.language_curriculum import (
    CurriculumOverviewOut,
    DailyMissionRenewOut,
    DailyPlanOut,
    ObjectivePracticeIn,
    ObjectivePracticeOut,
)
from app.schemas.language_certificate import LanguageCertificateListOut
from app.services.language_placement_service import (
    get_bank_with_responses,
    save_response,
    start_or_resume_attempt,
    submit_attempt,
    upload_speaking_audio,
)
from app.services.language_reading_service import (
    _lesson_focus,
    explain_sentence,
    grade_summary,
    get_reading_topics,
    next_reading,
    reading_glossary,
    reading_history,
    reading_insights,
    set_reading_topics,
)
from app.services.language_listening_journey.builder import build_listening_journey_bundle
from app.services.language_listening_lesson_experience.service import (
    build_student_lesson_bundle,
    build_submit_bundle,
)
from app.services.language_listening_service import (
    list_personalized_listening,
    next_listening,
    serialize_listening_lesson,
    skip_listening,
)
from app.services.language_listening_acquisition import acquire_next_listening
from app.services.language_listening_prefill_task import background_prefill_listening_pool
from app.services.language_skill_progress_service import submit_listening, submit_reading
from app.services.language_tts_service import get_lesson_audio
from app.services.language_rate_limit_service import check_or_raise
from app.services.language_adaptive_service import get_adaptive_state_overview
from app.services.language_learner_memory_service import get_memory, update_memory
from app.services.language_learner_model_service import LanguageLearnerModelService
from app.services.language_practice_service import generate_practice_set, submit_practice
from app.services.language_subscription_service import get_default_language, get_default_product, subscribe_language
from app.services.language_vocabulary_service import (
    analyze_word,
    assess_word_pronunciation,
    say_word,
    generate_vocabulary_challenge,
    get_vocabulary_card,
    list_vocabulary,
    review_vocabulary,
    save_word,
    submit_vocabulary_challenge,
)
from app.services.language_vocabulary_sr_service import get_vocabulary_stats
from app.services.language_writing_service import get_writing_prompt, list_writing, submit_writing
from app.services.language_writing.enums import OfficialWritingCEFR, WritingGoal
from app.services.language_writing_curriculum.goal_resolver import resolve_writing_goal
from app.services.language_writing_evaluation_runtime.runtime_api import submit_writing_draft_for_evaluation
from app.services.language_writing_journey.builder import build_writing_journey_bundle
from app.services.language_writing_runtime.runtime_api import generate_writing_lesson_for_student
from app.services.language_certificate_service import list_student_certificates

router = APIRouter(prefix="/student/languages", tags=["Language Learning"])
logger = logging.getLogger(__name__)


def _progress_out(row) -> LessonProgressOut:
    if not row:
        return LessonProgressOut()
    return LessonProgressOut(
        status=row.status.value if hasattr(row.status, "value") else str(row.status),
        score_percent=row.score_percent,
        completed_at=row.completed_at,
        attempt_count=int(row.attempt_count or 0),
    )


@router.get("/access", response_model=LanguageAccessOut)
async def language_access(
    student: User = Depends(require_student_actor()),
    db: AsyncSession = Depends(get_db),
):
    return await build_language_access(db, student.id)


@router.get("/product", response_model=LanguageProductOut)
async def language_product(db: AsyncSession = Depends(get_db)):
    product = await get_default_product(db)
    return LanguageProductOut(
        id=product.id,
        slug=product.slug,
        name_ar=product.name_ar,
        description_ar=product.description_ar,
        price=product.price,
        currency=product.currency,
        term_days=product.term_days,
    )


@router.post("/subscribe", response_model=LanguageSubscribeOut)
async def language_subscribe(
    body: LanguageSubscribeRequest,
    student: User = Depends(require_student_actor()),
    db: AsyncSession = Depends(get_db),
):
    result = await subscribe_language(db, student.id, body.method)
    await db.commit()
    return result


@router.post("/placement/start", response_model=PlacementStartOut)
async def placement_start(
    student: User = Depends(require_active_language_subscription()),
    db: AsyncSession = Depends(get_db),
):
    attempt_id, language_id = await start_or_resume_attempt(db, student_id=student.id)
    sections, questions, responses_by_qid = await get_bank_with_responses(
        db, student_id=student.id, attempt_id=attempt_id
    )
    attempt = await db.get(LanguagePlacementAttempt, attempt_id)
    await db.commit()
    return PlacementStartOut(
        attempt={
            "id": attempt_id,
            "language_id": language_id,
            "status": attempt.status.value if hasattr(attempt.status, "value") else str(attempt.status),
            "started_at": attempt.started_at,
            "submitted_at": attempt.submitted_at,
        },
        sections=[
            {
                "id": s.id,
                "skill": s.skill.value if hasattr(s.skill, "value") else str(s.skill),
                "title_ar": s.title_ar,
                "sort_order": s.sort_order,
            }
            for s in sections
        ],
        questions=[
            {
                "id": q.id,
                "section_id": q.section_id,
                "question_type": q.question_type,
                "prompt": q.prompt_json or {},
                "media_url": q.media_url,
                "max_points": q.max_points,
                "level_hint": q.level_hint,
                "sort_order": q.sort_order,
            }
            for q in questions
        ],
        responses_by_question_id=responses_by_qid,
    )


@router.put("/placement/responses", response_model=PlacementSaveResponseOut)
async def placement_save_response(
    body: PlacementSaveResponseIn,
    student: User = Depends(require_active_language_subscription()),
    db: AsyncSession = Depends(get_db),
):
    await save_response(
        db,
        student_id=student.id,
        attempt_id=body.attempt_id,
        question_id=body.question_id,
        response_json=body.response_json,
    )
    await db.commit()
    return PlacementSaveResponseOut(ok=True)


@router.post("/placement/speaking/upload", response_model=PlacementSpeakingUploadOut)
async def placement_upload_speaking(
    attempt_id: int = Form(...),
    question_id: int = Form(...),
    file: UploadFile = File(...),
    duration_seconds: int | None = Form(default=None),
    student: User = Depends(require_active_language_subscription()),
    db: AsyncSession = Depends(get_db),
):
    media = await upload_speaking_audio(
        db,
        student_id=student.id,
        attempt_id=attempt_id,
        question_id=question_id,
        file=file,
        duration_seconds=duration_seconds,
    )
    await db.commit()
    return PlacementSpeakingUploadOut(ok=True, media_object_id=media.id, public_url=media.public_url)


@router.post("/placement/submit", response_model=PlacementResultsOut)
async def placement_submit(
    body: PlacementSubmitIn,
    student: User = Depends(require_active_language_subscription()),
    db: AsyncSession = Depends(get_db),
):
    assessment, path_id = await submit_attempt(db, student_id=student.id, attempt_id=body.attempt_id)
    await db.commit()
    scores = await db.execute(select(LanguageAssessmentSkillScore).where(LanguageAssessmentSkillScore.assessment_id == assessment.id))
    rows = scores.scalars().all()
    # Surface which skill set the bottleneck overall level (tie -> first in LanguageSkill enum order).
    weakest_skill = None
    overall = assessment.overall_level
    if overall:
        order = {s: i for i, s in enumerate(LanguageSkill)}
        matching = sorted((r for r in rows if r.level == overall), key=lambda r: order.get(r.skill, 99))
        if matching:
            r0 = matching[0]
            weakest_skill = r0.skill.value if hasattr(r0.skill, "value") else str(r0.skill)
    return PlacementResultsOut(
        assessment_id=assessment.id,
        overall_level=assessment.overall_level.value if assessment.overall_level else None,
        overall_calculation_method=assessment.overall_calculation_method,
        completed_at=assessment.completed_at,
        weakest_skill=weakest_skill,
        skills=[
            {
                "skill": r.skill.value if hasattr(r.skill, "value") else str(r.skill),
                "score_percent": r.score_percent,
                "level": r.level.value if hasattr(r.level, "value") else str(r.level),
                "raw_metrics_json": r.raw_metrics_json,
                "ai_evaluation_json": r.ai_evaluation_json,
            }
            for r in rows
        ],
        path_id=path_id,
    )


@router.get("/hub", response_model=LanguageHubOut)
async def language_hub(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    return await build_language_hub(db, student_id=student.id)


@router.get("/curriculum", response_model=CurriculumOverviewOut)
async def language_curriculum(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    payload = await build_curriculum_overview(db, student_id=student.id)
    return CurriculumOverviewOut(**payload)


@router.get("/daily-plan", response_model=DailyPlanOut)
async def language_daily_plan(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    payload = await build_daily_mission(db, student_id=student.id)
    # Grant bounded XP for completed daily-mission tasks (round-scoped, reduced for renewed rounds).
    language = await get_default_language(db)
    await award_daily_mission_xp(db, student_id=student.id, language_id=language.id, plan=payload)
    # Phase 11 — record today's progress snapshot for analytics time-series (idempotent, best-effort).
    try:
        from app.services.language_progress_analytics_service import record_snapshot

        await record_snapshot(db, student_id=student.id, language_id=language.id)
    except Exception:
        pass
    await db.commit()
    return DailyPlanOut(**payload)


@router.post("/daily-plan/renew", response_model=DailyMissionRenewOut)
async def language_daily_plan_renew(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Renew the daily mission for a fresh round (only once the current one is finished).
    Renewed rounds award reduced XP, for integrity."""
    result = await renew_daily_mission(db, student_id=student.id)
    await db.commit()
    return DailyMissionRenewOut(**result)


@router.get("/xp")
async def language_xp(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    language = await get_default_language(db)
    return await get_xp_overview(db, student_id=student.id, language_id=language.id)


@router.post("/curriculum/objective/practiced", response_model=ObjectivePracticeOut)
async def language_curriculum_objective_practiced(
    body: ObjectivePracticeIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    result = await record_objective_practice(db, student_id=student.id, objective_id=body.objective_id)
    await db.commit()
    return ObjectivePracticeOut(**result)


@router.get("/curriculum/objective/{objective_id}/lesson")
async def language_objective_lesson(
    objective_id: str,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    return await get_micro_lesson(objective_id=objective_id)


@router.get("/adaptive/state")
async def language_adaptive_state(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    language = await get_default_language(db)
    result = await get_adaptive_state_overview(db, student_id=student.id, language_id=language.id)
    await db.commit()
    return result


@router.get("/reading", response_model=LessonListOut)
async def reading_list(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    student_level, lesson_level, items, progress_map = await list_lessons(
        db, student_id=student.id, skill=LanguageSkill.reading
    )
    lessons = [
        LessonListItemOut(
            id=item.id,
            title=item.title,
            level=item.level.value if item.level else (lesson_level.value if lesson_level else ""),
            sort_order=item.sort_order,
            progress=_progress_out(progress_map.get(item.id)),
        )
        for item in items
    ]
    return LessonListOut(
        student_level=student_level.value,
        lesson_level=lesson_level.value if lesson_level else None,
        lessons=lessons,
    )


@router.get("/listening", response_model=LessonListOut)
async def listening_list(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    language = await get_default_language(db)
    from app.services.language_progression_service import select_skill_level

    student_level = await select_skill_level(
        db,
        student_id=student.id,
        language_id=language.id,
        skill=LanguageSkill.listening,
        default=LanguageLevel.A2,
    )
    lesson_level_str, items, progress_map = await list_personalized_listening(
        db, student_id=student.id
    )
    out_lessons: list[LessonListItemOut] = []
    for item in items:
        _url, audio_available = await resolve_listening_audio(db, item)
        out_lessons.append(
            LessonListItemOut(
                id=item.id,
                title=item.title,
                level=item.level.value if item.level else lesson_level_str,
                sort_order=item.sort_order,
                progress=_progress_out(progress_map.get(item.id)),
                audio_available=audio_available,
            )
        )
    return LessonListOut(
        student_level=student_level.value,
        lesson_level=lesson_level_str,
        lessons=out_lessons,
    )


@router.get("/reading/next")
async def reading_next(
    length: str = "",
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Adaptive reading: the next passage at the student's level (generates content on demand).

    Optional ``length`` (short|medium|long) controls how long a freshly generated passage is.
    """
    lesson = await next_reading(db, student_id=student.id, length=length)
    if not lesson:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No reading content available yet")
    return lesson


@router.post("/reading/explain-sentence", response_model=ReadingExplainOut)
async def reading_explain_sentence(
    body: ReadingExplainIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Explain one sentence (meaning + a grammar note) for the learner's level."""
    return await explain_sentence(sentence=body.sentence, level=body.level)


@router.get("/learner/memory", response_model=LearnerMemoryOut)
async def learner_memory_get(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Learner-controlled memory profile (interests, goals, milestones)."""
    language = await get_default_language(db)
    payload = await get_memory(db, student_id=student.id, language_id=language.id)
    return LearnerMemoryOut(**payload)


@router.put("/learner/memory", response_model=LearnerMemoryOut)
async def learner_memory_update(
    body: LearnerMemoryUpdateIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Update learner-controlled memory fields."""
    language = await get_default_language(db)
    payload = await update_memory(
        db,
        student_id=student.id,
        language_id=language.id,
        updates=body.model_dump(exclude_unset=True),
    )
    await db.commit()
    return LearnerMemoryOut(**payload)


@router.get("/reading/topics", response_model=ReadingTopicsOut)
async def reading_topics_get(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Curated reading interests + the ones this learner picked."""
    return await get_reading_topics(db, student_id=student.id)


@router.put("/reading/topics", response_model=ReadingTopicsOut)
async def reading_topics_set(
    body: ReadingTopicsIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Save the learner's reading interests (drives generated-passage topics)."""
    result = await set_reading_topics(db, student_id=student.id, topics=body.topics)
    await db.commit()
    return result


@router.get("/reading/history", response_model=list[ReadingHistoryItemOut])
async def reading_history_list(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """The learner's reading library — passages they've completed, newest first."""
    return await reading_history(db, student_id=student.id)


@router.get("/reading/insights", response_model=ReadingInsightsOut)
async def reading_insights_get(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Reading analytics: WPM trend, comprehension, and per-skill strengths/gaps."""
    return await reading_insights(db, student_id=student.id)


@router.get("/reading/{content_id}/glossary")
async def reading_glossary_get(
    content_id: int,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Pre-computed definitions for the passage's words (so tapping any word is instant)."""
    result = await reading_glossary(db, student_id=student.id, content_id=content_id)
    await db.commit()
    return result


@router.get("/reading/{content_id}", response_model=ReadingLessonOut)
async def reading_detail(
    content_id: int,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    item, progress = await get_reading_lesson(db, student_id=student.id, content_id=content_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    body = lesson_body_for_student(item)
    focus = _lesson_focus(item)
    return ReadingLessonOut(
        id=item.id,
        title=item.title,
        level=item.level.value if item.level else "A1",
        passage=body.get("passage") or "",
        passage_ar=body.get("passage_ar"),
        glossary=body.get("glossary") or [],
        questions=body.get("questions") or [],
        progress=_progress_out(progress),
        **focus,
    )


@router.post("/reading/{content_id}/submit", response_model=LessonSubmitOut)
async def reading_submit(
    content_id: int,
    body: LessonSubmitIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    result = await submit_reading(
        db,
        student_id=student.id,
        content_id=content_id,
        answers=body.answers,
        duration_seconds=body.duration_seconds,
        activity_session_id=body.activity_session_id,
    )
    await db.commit()
    return LessonSubmitOut(**result)


@router.get("/reading/{content_id}/audio", response_model=ReadingAudioOut)
async def reading_audio(
    content_id: int,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Narration audio for a passage (read-along) — synthesized + cached on first request."""
    # Validate it's a reading lesson for this student before synthesizing — otherwise this would
    # voice (and thus leak) any content item, e.g. a listening clip's hidden transcript.
    item, _progress = await get_reading_lesson(db, student_id=student.id, content_id=content_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    tts = await get_lesson_audio(db, content_item_id=content_id)
    await db.commit()
    return ReadingAudioOut(public_url=(tts or {}).get("public_url"), available=bool(tts and tts.get("public_url")))


@router.post("/reading/{content_id}/summary", response_model=ReadingSummaryOut)
async def reading_summary(
    content_id: int,
    body: ReadingSummaryIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Grade the student's own-words summary of a passage for comprehension (AI)."""
    result = await grade_summary(db, student_id=student.id, content_id=content_id, summary=body.summary)
    await db.commit()
    return ReadingSummaryOut(**result)


@router.post("/vocabulary/save", response_model=VocabularySaveOut)
async def vocabulary_save(
    body: VocabularySaveIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Save a word the learner met (e.g. tapped while reading) to their vocabulary bank."""
    result = await save_word(db, student_id=student.id, word=body.word)
    await db.commit()
    return VocabularySaveOut(**result)


@router.get("/listening/journey", response_model=ListeningJourneyBundleOut)
async def listening_journey(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
    _deployment: None = Depends(require_listening_deployment_ready),
):
    """Canonical journey bundle — timeline, promotion, personal goal (no lesson playback)."""
    from app.services.language_subscription_service import get_default_language

    language = await get_default_language(db)
    return await build_listening_journey_bundle(
        db, student_id=student.id, language_id=language.id
    )


@router.get("/listening/next", response_model=ListeningNextResponseOut)
async def listening_next(
    background_tasks: BackgroundTasks,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
    _deployment: None = Depends(require_listening_deployment_ready),
    attempt: int = 1,
):
    """Adaptive listening session entry — always 200 with bundle or explicit acquisition state."""
    response, schedule_prefill = await acquire_next_listening(
        db, student_id=student.id, attempt=max(1, attempt)
    )
    if schedule_prefill:
        background_tasks.add_task(background_prefill_listening_pool, student_id=student.id)
    return response


@router.get("/listening/acquisition", response_model=ListeningNextResponseOut)
async def listening_acquisition_status(
    background_tasks: BackgroundTasks,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
    _deployment: None = Depends(require_listening_deployment_ready),
    attempt: int = 1,
):
    """Poll-friendly alias — same contract as /listening/next."""
    response, schedule_prefill = await acquire_next_listening(
        db, student_id=student.id, attempt=max(1, attempt)
    )
    if schedule_prefill:
        background_tasks.add_task(background_prefill_listening_pool, student_id=student.id)
    return response


@router.post("/listening/{content_id}/skip")
async def listening_skip(
    content_id: int,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
    _deployment: None = Depends(require_listening_deployment_ready),
):
    """Release the pinned lesson so the next /listening/next runs deterministic selection."""
    cleared = await skip_listening(db, student_id=student.id, content_id=content_id)
    return {"cleared": cleared}


@router.post("/listening/skip")
async def listening_skip_active(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
    _deployment: None = Depends(require_listening_deployment_ready),
):
    """Release whichever lesson is currently reserved (no content_id required)."""
    cleared = await skip_listening(db, student_id=student.id, content_id=None)
    return {"cleared": cleared}


@router.get("/listening/{content_id}", response_model=LessonExperienceBundleOut)
async def listening_detail(
    content_id: int,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
    _deployment: None = Depends(require_listening_deployment_ready),
):
    from app.services.language_listening_reservation import listening_session_reservation_service
    from app.services.language_subscription_service import get_default_language

    item, progress, _audio_url, _audio_available = await get_listening_lesson(
        db, student_id=student.id, content_id=content_id
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    language = await get_default_language(db)
    await listening_session_reservation_service.touch_started(
        db,
        student_id=student.id,
        language_id=language.id,
        content_item_id=content_id,
    )
    await db.commit()
    progress_out = _progress_out(progress).model_dump()
    bundle = await build_student_lesson_bundle(
        db,
        item=item,
        student_id=student.id,
        language_id=language.id,
        progress_out=progress_out,
    )
    return bundle


@router.post("/listening/{content_id}/submit", response_model=ListeningLessonSubmitBundleOut)
async def listening_submit(
    content_id: int,
    body: LessonSubmitIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
    _deployment: None = Depends(require_listening_deployment_ready),
):
    from app.services.language_subscription_service import get_default_language

    result = await submit_listening(
        db,
        student_id=student.id,
        content_id=content_id,
        answers=body.answers,
        activity_session_id=body.activity_session_id,
    )
    await db.commit()
    item, progress, _url, _avail = await get_listening_lesson(
        db, student_id=student.id, content_id=content_id
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    language = await get_default_language(db)
    progress_out = _progress_out(progress).model_dump()
    return await build_submit_bundle(
        db,
        item=item,
        student_id=student.id,
        language_id=language.id,
        progress_out=progress_out,
        submit_result=result,
    )


@router.get("/progress", response_model=LanguageProgressOut)
async def language_progress(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    return await build_language_progress(db, student_id=student.id)


@router.get("/vocabulary", response_model=VocabularyListOut)
async def vocabulary_list(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    return await list_vocabulary(db, student_id=student.id)


@router.get("/vocabulary/stats")
async def vocabulary_stats(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    language = await get_default_language(db)
    return await get_vocabulary_stats(db, student_id=student.id, language_id=language.id)


@router.post("/vocabulary/analyze", response_model=WordAnalysisOut)
async def vocabulary_analyze(
    body: WordAnalysisIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """On-demand AI vocabulary lookup: definition, example, pronunciation, synonyms (English only)."""
    return await analyze_word(word=body.word, level=body.level)


class VocabBatchIn(BaseModel):
    topic: str | None = None
    level: str | None = None


@router.get("/vocabulary/generator/options")
async def vocabulary_generator_options(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Available topics + CEFR levels for the infinite vocabulary generator (offline, no LLM)."""
    from app.services.language_vocabulary_catalog_service import get_options

    return await get_options(db)


@router.post("/vocabulary/generate-batch")
async def vocabulary_generate_batch(
    body: VocabBatchIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """A fresh random batch of unseen words (offline). Filters out words this learner has already seen."""
    from app.services.language_vocabulary_catalog_service import generate_batch

    try:
        result = await generate_batch(db, student_id=student.id, topic=body.topic, level=body.level)
        await db.commit()
        return result
    except Exception:
        await db.rollback()
        logger.warning("vocabulary generate-batch failed", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not generate a batch right now. Please try again.",
        )


class WordSayIn(BaseModel):
    word: str


@router.post("/vocabulary/say")
async def vocabulary_say(
    body: WordSayIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Hear the word: synthesize its pronunciation (edge-tts, no quota)."""
    return await say_word(body.word)


@router.post("/vocabulary/pronounce")
async def vocabulary_pronounce(
    word: str = Form(...),
    file: UploadFile = File(...),
    duration_seconds: int | None = Form(default=None),
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Say the word: AI grades pronunciation + flags if a different word was said."""
    check_or_raise("speaking", student.id)
    data = await file.read()
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The audio file is empty")
    suffix = ".webm"
    if file.filename and "." in file.filename:
        suffix = "." + file.filename.rsplit(".", 1)[-1].lower()
    language = await get_default_language(db)
    result = await assess_word_pronunciation(
        db, student_id=student.id, language_id=language.id, word=word, data=data, suffix=suffix
    )
    await db.commit()
    return result


@router.get("/vocabulary/challenge", response_model=VocabularyChallengeOut)
async def vocabulary_challenge(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Daily fill-in-the-blanks challenge built from the student's due vocabulary (English only)."""
    return await generate_vocabulary_challenge(db, student_id=student.id)


@router.post("/vocabulary/challenge/submit", response_model=VocabularyChallengeSubmitOut)
async def vocabulary_challenge_submit(
    body: VocabularyChallengeSubmitIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Record a finished daily challenge as learner-model evidence (source='daily')."""
    result = await submit_vocabulary_challenge(
        db,
        student_id=student.id,
        results=[r.model_dump() for r in body.results],
        activity_session_id=body.activity_session_id,
    )
    await db.commit()
    return result


@router.get("/learner-model/profile", response_model=LearnerModelProfileOut)
async def learner_model_profile(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Unified learner-model snapshot: component mastery, per-skill confidence, due-review count."""
    language = await get_default_language(db)
    service = LanguageLearnerModelService(db)
    components = await service.get_component_profile(student_id=student.id, language_id=language.id)
    skill_confidence = await service.get_skill_confidence(student_id=student.id, language_id=language.id)
    due = await service.get_due_reviews(student_id=student.id, language_id=language.id)
    return {"components": components, "skill_confidence": skill_confidence, "due_count": len(due)}


@router.get("/learner-model/practice", response_model=LearnerPracticeSetOut)
async def learner_model_practice(
    count: int = 4,
    skill: str = "",
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Adaptive 'smart review': MCQs targeting the learner's weakest knowledge components.

    Optional ``skill`` drills one skill (reading/listening/writing/speaking).
    """
    return await generate_practice_set(db, student_id=student.id, count=count, skill=skill)


@router.post("/learner-model/practice/submit", response_model=LearnerPracticeSubmitOut)
async def learner_model_practice_submit(
    body: LearnerPracticeSubmitIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    """Record answered smart-review questions as learner-model evidence (source='daily')."""
    result = await submit_practice(
        db, student_id=student.id, results=[r.model_dump() for r in body.results]
    )
    await db.commit()
    return result


@router.get("/dictionary", response_model=DictionarySearchOut)
async def dictionary_search(
    q: str = "",
    student: User = Depends(require_active_language_subscription()),
):
    """Global English dictionary (WordNet): word definitions + synonyms + prefix suggestions."""
    from fastapi.concurrency import run_in_threadpool

    from app.services.language_dictionary_service import search

    return await run_in_threadpool(search, q)


@router.get("/vocabulary/{content_id}", response_model=VocabularyCardOut)
async def vocabulary_detail(
    content_id: int,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    return await get_vocabulary_card(db, student_id=student.id, content_id=content_id)


@router.post("/vocabulary/{content_id}/review", response_model=VocabularyCardOut)
async def vocabulary_review(
    content_id: int,
    body: VocabularyReviewIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    result = await review_vocabulary(db, student_id=student.id, content_id=content_id, quality=body.quality)
    await db.commit()
    return result


@router.get("/writing", response_model=WritingListOut)
async def writing_list(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    return await list_writing(db, student_id=student.id)


@router.get("/writing/journey", response_model=WritingJourneyBundleOut)
async def writing_journey(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    language = await get_default_language(db)
    return await build_writing_journey_bundle(
        db,
        student_id=student.id,
        language_id=language.id,
    )


@router.post("/writing/generate", response_model=WritingGenerateOut)
async def writing_generate(
    body: WritingGenerateIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    goal = resolve_writing_goal(body.goal) if body.goal else None
    cefr = OfficialWritingCEFR(body.official_cefr) if body.official_cefr else None
    result = await generate_writing_lesson_for_student(
        db,
        student_id=student.id,
        goal=goal,
        chain_id=body.chain_id,
        node_id=body.node_id,
        official_cefr=cefr,
    )
    await db.commit()
    return result


@router.post("/writing/{content_item_id}/draft", response_model=WritingDraftSubmitOut)
async def writing_submit_draft(
    content_item_id: int,
    body: WritingDraftSubmitIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    language = await get_default_language(db)
    result = await submit_writing_draft_for_evaluation(
        db,
        student_id=student.id,
        content_item_id=content_item_id,
        draft_text=body.draft_text,
        complete_if_ready=body.complete_if_ready,
        language_id=language.id,
    )
    await db.commit()
    return result


@router.get("/writing/{prompt_id}", response_model=WritingPromptOut)
async def writing_detail(
    prompt_id: int,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    return await get_writing_prompt(db, student_id=student.id, prompt_id=prompt_id)


@router.post("/writing/{prompt_id}/submit", response_model=WritingSubmitOut)
async def writing_submit(
    prompt_id: int,
    body: WritingSubmitIn,
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    result = await submit_writing(
        db,
        student_id=student.id,
        prompt_id=prompt_id,
        response_text=body.response_text,
        activity_session_id=body.activity_session_id,
    )
    await db.commit()
    return WritingSubmitOut(**result)


@router.get("/certificates", response_model=LanguageCertificateListOut)
async def certificates_list(
    student: User = Depends(require_language_learning_ready()),
    db: AsyncSession = Depends(get_db),
):
    payload = await list_student_certificates(db, student_id=student.id)
    await db.commit()
    return LanguageCertificateListOut(**payload)
