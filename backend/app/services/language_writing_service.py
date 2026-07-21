"""Writing prompts — Phase 1 rule-based scoring (no AI)."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.language.enums import LanguageSkill
from app.models.language.progress import LanguageWritingProgress
from app.services.language_adaptive_service import record_lesson_result
from app.services.language_analytics_service import refresh_language_analytics
from app.services.language_content_service import get_content_item, list_content_items, pass_threshold_for_item
from app.services.language_curriculum_service import credit_skill_objectives
from app.services.language_engagement_service import record_activity
from app.services.language_learner_events import record_scored_practice
from app.services.language_validation import count_sentences, validate_writing_submission
from app.services.language_placement_ai_scoring import score_writing_ai
from app.services.language_placement_scoring_service import score_writing
from app.services.language_subscription_service import get_default_language

CONTENT_TYPE = "writing_prompt"


def _sentence_count(text: str) -> int:
    return count_sentences(text)


async def _writing_progress_map(db: AsyncSession, *, student_id: int, ids: list[int]) -> dict[int, LanguageWritingProgress]:
    if not ids:
        return {}
    result = await db.execute(
        select(LanguageWritingProgress).where(
            LanguageWritingProgress.student_id == student_id,
            LanguageWritingProgress.content_item_id.in_(ids),
        )
    )
    return {p.content_item_id: p for p in result.scalars().all()}


def _prompt_out(item, progress: LanguageWritingProgress | None) -> dict:
    body = item.body_json or {}
    return {
        "id": item.id,
        "title": item.title,
        "level": item.level.value if item.level else None,
        "prompt": body.get("prompt") or "",
        "prompt_ar": body.get("prompt_ar"),
        "min_words": int(body.get("min_words") or 20),
        "min_sentences": int(body.get("min_sentences") or 2),
        "progress": {
            "submitted_text": progress.submitted_text if progress else None,
            "word_count": progress.word_count if progress else 0,
            "score_percent": progress.score_percent if progress else None,
            "completed_at": progress.completed_at if progress else None,
            "submitted_at": progress.submitted_at if progress else None,
        },
    }


async def list_writing(db: AsyncSession, *, student_id: int) -> dict:
    student_level, lesson_level, items = await list_content_items(
        db,
        student_id=student_id,
        content_type=CONTENT_TYPE,
        skill=LanguageSkill.writing,
        level_skill=LanguageSkill.writing,
    )
    prog = await _writing_progress_map(db, student_id=student_id, ids=[i.id for i in items])
    return {
        "student_level": student_level.value,
        "lesson_level": lesson_level.value if lesson_level else None,
        "prompts": [_prompt_out(i, prog.get(i.id)) for i in items],
    }


async def get_writing_prompt(db: AsyncSession, *, student_id: int, prompt_id: int) -> dict:
    item = await get_content_item(
        db,
        student_id=student_id,
        content_id=prompt_id,
        content_type=CONTENT_TYPE,
        skill=LanguageSkill.writing,
        level_skill=LanguageSkill.writing,
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise is not available")
    prog = await _writing_progress_map(db, student_id=student_id, ids=[item.id])
    return _prompt_out(item, prog.get(item.id))


async def submit_writing(
    db: AsyncSession,
    *,
    student_id: int,
    prompt_id: int,
    response_text: str,
    activity_session_id: str | None = None,
) -> dict:
    item = await get_content_item(
        db,
        student_id=student_id,
        content_id=prompt_id,
        content_type=CONTENT_TYPE,
        skill=LanguageSkill.writing,
        level_skill=LanguageSkill.writing,
    )
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise is not available")
    body = item.body_json or {}
    min_words = int(body.get("min_words") or 20)
    min_sentences = int(body.get("min_sentences") or 2)
    text, wc, sc = validate_writing_submission(
        response_text,
        min_words=min_words,
        min_sentences=min_sentences,
    )

    # Real CEFR grading when available; otherwise the rule heuristic. Track which one ran.
    prompt_text = body.get("prompt") or body.get("instructions") or ""
    ai_writing = await score_writing_ai(text=text, prompt=prompt_text)
    if ai_writing:
        score_pct, metrics = ai_writing
        scoring_version = "ai_rubric_v2"
    else:
        score_pct, metrics = score_writing({"text": text}, min_words=min_words)
        scoring_version = "rule_v1"
    metrics["sentence_count"] = sc
    metrics["min_sentences"] = min_sentences
    threshold = pass_threshold_for_item(item)
    passed = score_pct >= threshold and wc >= min_words and sc >= min_sentences

    result = await db.execute(
        select(LanguageWritingProgress).where(
            LanguageWritingProgress.student_id == student_id,
            LanguageWritingProgress.content_item_id == prompt_id,
        )
    )
    progress = result.scalar_one_or_none()
    if not progress:
        progress = LanguageWritingProgress(student_id=student_id, content_item_id=prompt_id, submitted_text=text)
        db.add(progress)
    progress.submitted_text = text
    progress.word_count = wc
    progress.score_percent = float(score_pct)
    progress.metrics_json = metrics
    progress.scoring_version = scoring_version
    if passed and not progress.completed_at:
        progress.completed_at = datetime.now(timezone.utc)
    await db.flush()

    language = await get_default_language(db)
    event = "writing_completed" if passed else "writing_submitted"
    await record_activity(
        db,
        student_id=student_id,
        language_id=language.id,
        event_type=event,
        skill=LanguageSkill.writing,
        payload_json={
            "content_item_id": prompt_id,
            "title": item.title,
            "score_percent": score_pct,
            "passed": passed,
        },
    )
    await refresh_language_analytics(db, student_id=student_id, language_id=language.id)
    await record_lesson_result(
        db, student_id=student_id, language_id=language.id, skill=LanguageSkill.writing, score_percent=float(score_pct)
    )
    await credit_skill_objectives(
        db, student_id=student_id, language_id=language.id, skill=LanguageSkill.writing,
        score_percent=float(score_pct), passed=passed,
    )
    if passed:
        from app.services.language_xp_service import award_language_xp

        await award_language_xp(db, student_id=student_id, language_id=language.id, activity="writing", key=f"writing:{prompt_id}")
    await record_scored_practice(
        db, student_id=student_id, language_id=language.id, skill=LanguageSkill.writing,
        level=item.level, score_percent=float(score_pct), source="writing",
    )
    # Wave D: attested session only (never trust body_json grammar stamp alone).
    grammar_id = None
    session_id = activity_session_id or str((body or {}).get("activity_session_id") or "")
    if session_id:
        from app.services.language_grammar_integrity import (
            AttestedCompletionRequest,
            GrammarIntegrityError,
            complete_attested_activity,
            load_owned_open_session,
        )

        try:
            session = await load_owned_open_session(
                db, activity_session_id=session_id, student_id=student_id
            )
            if session.content_item_id is not None and int(session.content_item_id) != int(prompt_id):
                raise GrammarIntegrityError(
                    "activity_ownership",
                    "Activity session does not match this writing prompt",
                )
            completion = await complete_attested_activity(
                db,
                AttestedCompletionRequest(
                    student_id=student_id,
                    language_id=language.id,
                    activity_session_id=session_id,
                    response_text=text,
                    server_score=float(score_pct),
                ),
            )
            grammar_id = completion.grammar_id
        except GrammarIntegrityError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    return {
        "prompt_id": prompt_id,
        "score_percent": float(score_pct),
        "passed": passed,
        "word_count": wc,
        "sentence_count": sc,
        "grammar_id": grammar_id,
        "completed_at": progress.completed_at,
        "status": "completed" if progress.completed_at else "in_progress",
    }
