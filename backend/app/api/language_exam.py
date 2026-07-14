"""5-section AI placement exam — a section-based, partly audio-native state machine.

Sections run in order: SPEAKING (audio-native via google-genai) -> LISTENING (adaptive audio MCQ)
-> READING (adaptive passage MCQ) -> WRITING (free text, AI-graded) -> INTERVIEW (Phase-2 guided
spoken follow-up seeded by Phase-1 evidence). Reading/listening/writing content is generated fresh
per attempt in a background task while the student does speaking. When the last section finishes, a
background task fuses everything into a per-skill CEFR report and unlocks the module.

The whole flow is driven by one ``exam_state`` JSON blob on the session row, and the frontend is
told exactly what to render next via the unified ``ExamStateOut`` contract:

  POST /initiate              -> resume an open exam, or build a fresh one (returns first state)
  GET  /{id}/state           -> current state (resume/polling; self-heals stalled content prep)
  POST /{id}/speaking/turn   -> (multipart audio) assess one spoken answer; speaking OR interview
  POST /{id}/answer          -> (MCQ) record a listening/reading answer; adaptive next/advance
  POST /{id}/writing         -> (text) record the writing answer; flow into the interview
  POST /{id}/abandon         -> drop an unfinished attempt so a fresh one can start
  GET  /{id}/report          -> poll for the final per-skill report
"""

from __future__ import annotations

import asyncio
import copy
import hashlib
import json
import logging
import secrets
import unicodedata
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.core.config import get_settings
from app.db.session import AsyncSessionLocal, get_db
from app.models.language.analytics import LanguageAnalytics
from app.models.language.content import LanguageContentItem
from app.models.language.enums import LanguageLevel, LanguageOnboardingStep, LanguageSkill
from app.models.language.exam import LanguageExamSession
from app.models.language.profile import LanguageStudentProfile
from app.models.profile import StudentProfile
from app.models.user import User
from app.schemas.language_exam import (
    CEFRLevel,
    ExamProcessingOut,
    ExamReportOut,
    ExamStateOut,
    McqAnswerIn,
    McqPromptOut,
    MultiSkillReportSchema,
    SpeakingPromptOut,
    SpeakingTurnFeedbackOut,
    WritingAnswerIn,
    WritingPromptOut,
)
from app.services.language_access_service import require_active_language_subscription
from app.services.language_audio_security_service import ValidatedAudio, validate_placement_audio
from app.services.language_exam_service import (
    ALL_CEFR_LEVELS,
    adaptive_next_level,
    adaptive_result,
    ai_engine,
    build_verified_speaking_evidence,
    cefr_from_rank,
    cefr_rank,
    overall_level,
)
from app.services.language_level_utils import primary_focus_and_strength
from app.services.language_placement_policy_service import (
    ensure_placement_retake_allowed,
    next_allowed_retake_at,
)
from app.services.language_placement_question_bank_service import (
    BoundaryTarget,
    bank_item_to_exam_item,
    record_bank_item_answer,
    select_placement_bank_items,
)
from app.services.language_rate_limit_service import check, check_or_raise
from app.services.language_subscription_service import ensure_language_profile, get_default_language
from app.services.language_transcription_service import transcribe_english_audio
from app.services.language_tts_service import synthesize_exam_audio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/student/languages/exam", tags=["Language Exam"])

SECTIONS = ["speaking", "listening", "reading", "grammar_vocab", "writing"]
# Sections that work like the audio speaking flow (record -> assess -> next question).
# "interview" stays in this set (not in SECTIONS) so any already-persisted session that still
# has "interview" in its own exam_state["sections"] continues to route those turns correctly.
SPEAKING_LIKE = {"speaking", "interview"}
MCQ_SECTIONS = {"listening", "reading", "grammar_vocab"}
PREPARED_SECTIONS = {"listening", "reading", "grammar_vocab", "writing"}
SPEAKING_TURNS = 3
INTERVIEW_TURNS = 2  # Phase 2 — guided follow-up seeded by Phase 1 evidence.
ADAPTIVE_MAX_STEPS = 5  # MCQ sections: max adaptive questions before settling on a level.
MIN_MCQ_EVIDENCE_ITEMS = 3  # MCQ sections: don't settle on a level from fewer answered items than this.
WRITING_MIN_WORDS = 40
EVALUATION_LEASE_SECONDS = 15 * 60


# ---------------------------------------------------------------------------------------
# level / content helpers
# ---------------------------------------------------------------------------------------

async def _effective_level(db: AsyncSession, *, student_id: int, language_id: int) -> str:
    analytics = await db.get(LanguageAnalytics, {"student_id": student_id, "language_id": language_id})
    if analytics and analytics.speaking_level:
        return analytics.speaking_level.value
    return "A2"


async def _student_grade(db: AsyncSession, *, student_id: int) -> int | None:
    return (
        await db.execute(select(StudentProfile.grade).where(StudentProfile.user_id == student_id).limit(1))
    ).scalar_one_or_none()


def _new_adaptive_section(pool: dict[str, dict], start_level: str) -> dict:
    """Build the adaptive section state. Starts at the nearest available level to the estimate."""
    if pool and start_level not in pool:
        # Snap to the closest available rung.
        start_level = min(pool.keys(), key=lambda lv: abs(cefr_rank(CEFRLevel(lv)) - cefr_rank(CEFRLevel(start_level))))
    tokenized_pool = {
        level: {**item, "question_token": str(item.get("question_token") or _new_exam_token())}
        for level, item in pool.items()
    }
    return {
        "mode": "adaptive",
        "pool": tokenized_pool,
        "current_level": start_level if tokenized_pool else "",
        "start_level": start_level,
        "asked": [],
        "max_steps": ADAPTIVE_MAX_STEPS,
        "ready": bool(tokenized_pool),
        "done": False,
        "evidence_status": "missing_student_response" if tokenized_pool else "content_unavailable",
    }


def _new_exam_token() -> str:
    """Return an opaque per-prompt token; it is never derived from a database identifier."""
    return secrets.token_urlsafe(24)


def _state_revision(state: dict) -> int:
    try:
        return max(1, int(state.get("state_revision") or 1))
    except (TypeError, ValueError):
        return 1


def _bump_state_revision(state: dict) -> int:
    revision = _state_revision(state) + 1
    state["state_revision"] = revision
    return revision


def _ensure_state_protocol(state: dict) -> bool:
    """Upgrade an existing JSON state in-place without changing historical answers."""
    changed = False
    if not isinstance(state.get("state_revision"), int) or int(state.get("state_revision") or 0) < 1:
        state["state_revision"] = 1
        changed = True
    for section in MCQ_SECTIONS:
        for item in (state.get(section, {}).get("pool") or {}).values():
            if not item.get("question_token"):
                item["question_token"] = _new_exam_token()
                changed = True
    for section in SPEAKING_LIKE:
        spoken = state.get(section, {})
        if spoken.get("pending_question") and not spoken.get("turn_token"):
            spoken["turn_token"] = _new_exam_token()
            changed = True
    writing = state.get("writing", {})
    if writing.get("prompt") and not writing.get("prompt_token"):
        writing["prompt_token"] = _new_exam_token()
        changed = True
    return changed


def _is_usable_audio_url(url: str | None) -> bool:
    value = str(url or "").strip()
    if not value:
        return False
    if value.startswith("/uploads/"):
        return True
    if value.startswith("http://") or value.startswith("https://"):
        return True
    return value.startswith("/language-assets/en/placement/listening/")


def _listening_text_from_body(body: dict | None) -> str:
    text = (
        (body or {}).get("audio_transcript")
        or (body or {}).get("text")
        or (body or {}).get("passage")
        or ""
    )
    return str(text).strip()


def _first_question(body: dict | None) -> dict | None:
    for q in (body or {}).get("questions") or []:
        choices = q.get("choices")
        ci = q.get("correct_index")
        # The correct index must point at a real option, else the item is unanswerable and would
        # always grade wrong, dragging the adaptive staircase down.
        if isinstance(choices, list) and len(choices) >= 2 and isinstance(ci, int) and 0 <= ci < len(choices):
            return q
    return None


async def _seeded_pool(
    db: AsyncSession, *, language_id: int, skill: LanguageSkill, levels: list[str]
) -> dict[str, dict]:
    """Seeded-bank fallback: one comprehension item per CEFR level -> {level: item}."""
    pool: dict[str, dict] = {}
    for lvl in levels:
        q = (
            select(LanguageContentItem)
            .where(
                LanguageContentItem.language_id == language_id,
                LanguageContentItem.skill == skill,
                LanguageContentItem.content_type == "lesson",
                LanguageContentItem.level == LanguageLevel(lvl),
                LanguageContentItem.is_published.is_(True),
            )
            .order_by(func.random())
            .limit(8)
        )
        for row in (await db.execute(q)).scalars().all():
            question = _first_question(row.body_json)
            if not question:
                continue
            body = row.body_json or {}
            audio_url = body.get("audio_url") if _is_usable_audio_url(body.get("audio_url")) else None
            audio_text = _listening_text_from_body(body)
            if skill == LanguageSkill.listening and not audio_url and not audio_text:
                continue
            item = {
                "content_id": row.id,
                "level": lvl,
                "passage": (body.get("passage") or body.get("text") or ""),
                "situation": (body.get("situation") or ""),
                "question": question.get("stem", ""),
                "options": list(question.get("choices") or []),
                "correct_index": int(question.get("correct_index")),
            }
            if audio_url:
                item["audio_url"] = str(audio_url)
            if audio_text:
                item["audio_text"] = audio_text
            pool[lvl] = item
            break
    return pool


def _is_valid_mcq_item(item: dict) -> bool:
    options = item.get("options")
    ci = item.get("correct_index")
    return isinstance(options, list) and len(options) >= 2 and isinstance(ci, int) and 0 <= ci < len(options)


def _already_used_bank_item_ids(state: dict, skill: str) -> set[int]:
    """Bank item ids already asked for this skill in this exam session (session-scoped, P1.1).

    Reads state[skill]["asked"] only — sections with no "asked" list (e.g. "writing") naturally
    yield an empty set. Does not touch usage_count/correct_count or any lifetime/cross-session
    history."""
    asked = state.get(skill, {}).get("asked", []) or []
    return {int(a["bank_item_id"]) for a in asked if a.get("bank_item_id")}


def _mcq_continuation_level(
    *, pool_levels: set[str], asked_levels: set[str], asked_count: int, current: str
) -> str | None:
    """When the adaptive staircase converges/plateaus, decide whether to keep probing instead of
    settling on a level (P1.2 minimum evidence floor).

    Returns the next unasked pool level to ask (nearest to `current` by CEFR rank distance, same
    selection style as _new_adaptive_section's initial-level snap), or None if evidence is already
    sufficient (asked_count >= MIN_MCQ_EVIDENCE_ITEMS) or the pool has no unasked levels left — in
    which case the caller should fall through to its existing completion path."""
    if asked_count >= MIN_MCQ_EVIDENCE_ITEMS:
        return None
    remaining = [lv for lv in pool_levels if lv not in asked_levels]
    if not remaining:
        return None
    return min(remaining, key=lambda lv: abs(cefr_rank(CEFRLevel(lv)) - cefr_rank(CEFRLevel(current))))


def _boundary_situation(asked: list[dict]) -> tuple[str, str] | None:
    """Detect uncertainty between two adjacent CEFR levels from the two most-recently-answered
    items: one correct and the other, at the adjacent level, incorrect (P1.3).

    Returns the (low, high) level strings to confirm, or None if the last two answers don't
    straddle a single-band boundary (fewer than 2 answered, non-adjacent levels, or matching
    correctness — agreement isn't uncertainty)."""
    if len(asked) < 2:
        return None
    a, b = asked[-2], asked[-1]
    if bool(a.get("correct")) == bool(b.get("correct")):
        return None
    try:
        rank_a = cefr_rank(CEFRLevel(a["level"]))
        rank_b = cefr_rank(CEFRLevel(b["level"]))
    except ValueError:
        return None
    if abs(rank_a - rank_b) != 1:
        return None
    return (a["level"], b["level"]) if rank_a < rank_b else (b["level"], a["level"])


async def _boundary_confirmation_item(
    db: AsyncSession, *, language_id: int, skill: str, low: str, high: str, used_item_ids: set[int]
) -> dict | None:
    """Fetch one genuine boundary-tagged bank item for the (low, high) CEFR pair (P1.3), or None
    if the bank has no such item.

    select_placement_bank_items() falls back to a plain level-matched item when no boundary item
    exists, so the returned row's own boundary_low_level/boundary_high_level are checked here to
    confirm it's a real boundary hit and not that fallback in disguise."""
    boundary = BoundaryTarget(low=LanguageLevel(low), high=LanguageLevel(high))
    rows = await select_placement_bank_items(
        db,
        language_id=language_id,
        skill=skill,
        level=high,
        count=1,
        used_item_ids=used_item_ids,
        boundary=boundary,
    )
    if not rows:
        return None
    row = rows[0]
    if row.boundary_low_level != boundary.low or row.boundary_high_level != boundary.high:
        return None

    item = bank_item_to_exam_item(row)
    if not _is_valid_mcq_item(item):
        return None
    if skill == "listening":
        if not _is_usable_audio_url(item.get("audio_url")):
            item["audio_url"] = None
        body = item.get("body") or {}
        audio_text = _listening_text_from_body(body)
        if item.get("content_id"):
            content = await db.get(LanguageContentItem, item["content_id"])
            body = content.body_json if content else body
            if not audio_text:
                audio_text = _listening_text_from_body(body)
        audio_url = (body or {}).get("audio_url")
        if not item.get("audio_url") and audio_text and _is_usable_audio_url(audio_url):
            item["audio_url"] = str(audio_url)
        if audio_text:
            item["audio_text"] = audio_text
        if not item.get("audio_url") and not item.get("audio_text"):
            return None
    item["source"] = "placement_qbank"
    return item


async def _question_bank_pool(
    db: AsyncSession,
    *,
    language_id: int,
    skill: str,
    levels: list[str],
    used_item_ids: set[int] | None = None,
) -> dict[str, dict]:
    """Reviewed question-bank items: one internal MCQ item per requested CEFR level."""
    pool: dict[str, dict] = {}
    for lvl in levels:
        for row in await select_placement_bank_items(
            db,
            language_id=language_id,
            skill=skill,
            level=lvl,
            count=4 if skill == "listening" else 1,
            used_item_ids=used_item_ids,
        ):
            item = bank_item_to_exam_item(row)
            if not _is_valid_mcq_item(item):
                continue
            if skill == "listening":
                if not _is_usable_audio_url(item.get("audio_url")):
                    item["audio_url"] = None
                body = item.get("body") or {}
                audio_text = _listening_text_from_body(body)
                if item.get("content_id"):
                    content = await db.get(LanguageContentItem, item["content_id"])
                    body = content.body_json if content else body
                    if not audio_text:
                        audio_text = _listening_text_from_body(body)
                audio_url = (body or {}).get("audio_url")
                if not item.get("audio_url") and audio_text and _is_usable_audio_url(audio_url):
                    item["audio_url"] = str(audio_url)
                if audio_text:
                    item["audio_text"] = audio_text
                if not item.get("audio_url") and not item.get("audio_text"):
                    continue
            item["source"] = "placement_qbank"
            pool[lvl] = item
            break
    return pool


async def _generated_pool(
    db: AsyncSession, *, language_id: int, levels: list[str]
) -> dict[str, dict]:
    """Last-resort fallback: verified AI-generated questions (no passage) -> {level: item}.

    Consumes the offline-built, second-LLM-verified `LanguageGeneratedQuestion` bank so a level is
    never left without a question when neither AI generation nor the passage-based lesson bank could
    supply one. Standalone (passage-less) use-of-English items, so reading-only.
    """
    from app.models.language.learner_model import LanguageGeneratedQuestion

    pool: dict[str, dict] = {}
    for lvl in levels:
        row = (
            await db.execute(
                select(LanguageGeneratedQuestion)
                .where(
                    LanguageGeneratedQuestion.language_id == language_id,
                    LanguageGeneratedQuestion.cefr_level == LanguageLevel(lvl),
                    LanguageGeneratedQuestion.verified.is_(True),
                )
                .order_by(func.random())
                .limit(1)
            )
        ).scalar_one_or_none()
        if not row:
            continue
        prompt = row.prompt_json or {}
        choices = prompt.get("choices") or []
        ci = prompt.get("correct_index")
        if len(choices) < 2 or not isinstance(ci, int) or not (0 <= ci < len(choices)):
            continue
        pool[lvl] = {
            "level": lvl,
            "passage": "",
            "situation": "",
            "question": prompt.get("stem", ""),
            "options": list(choices),
            "correct_index": int(prompt.get("correct_index")),
        }
    return pool


async def _mark_content_prep_unavailable(
    *, session_id: str, prep_token: str, error_code: str
) -> None:
    async with AsyncSessionLocal() as mark_db:
        sess = (
            await mark_db.execute(
                select(LanguageExamSession)
                .where(LanguageExamSession.id == session_id)
                .with_for_update()
            )
        ).scalar_one_or_none()
        if not sess or sess.status != "in_progress":
            return
        state = copy.deepcopy(sess.exam_state or {})
        if str(state.get("content_prep_token") or "") != prep_token:
            return
        state["content_prep_status"] = "content_unavailable"
        state["content_prep_error_code"] = error_code
        for section in PREPARED_SECTIONS:
            if not state.get(section, {}).get("ready"):
                state.setdefault(section, {})["evidence_status"] = "content_unavailable"
        _bump_state_revision(state)
        sess.exam_state = state
        flag_modified(sess, "exam_state")
        await mark_db.commit()


async def _prepare_content(session_id: str, language_id: int, level: str) -> None:
    """Prepare placement content in two phases without a DB transaction during AI/TTS.

    Phase one snapshots all database-backed candidates and closes its transaction.  Phase two runs
    external generation and TTS using only detached dictionaries, then merges only the prepared
    sections into the latest JSON state under a short row lock.
    """
    prep_token = ""
    source_revision = 1
    l_pool: dict[str, dict] = {}
    try:
        # Database-only preparation.  Do not add AI/TTS calls inside this context.
        async with AsyncSessionLocal() as db:
            sess = await db.get(LanguageExamSession, session_id)
            if not sess or not sess.exam_state or sess.status != "in_progress":
                return
            source_state = copy.deepcopy(sess.exam_state or {})
            source_revision = _state_revision(source_state)
            prep_token = str(source_state.get("content_prep_token") or "")
            student_id = int(sess.student_id)
            if not check("placement_generation", f"{student_id}:{session_id}"):
                logger.warning(
                    "Placement content generation rate-limited session_id=%s user_id=%s",
                    session_id,
                    student_id,
                )
                await db.rollback()
                await _mark_content_prep_unavailable(
                    session_id=session_id,
                    prep_token=prep_token,
                    error_code="content_generation_rate_limited",
                )
                return

            r_pool = await _question_bank_pool(
                db, language_id=language_id, skill="reading", levels=ALL_CEFR_LEVELS,
                used_item_ids=_already_used_bank_item_ids(source_state, "reading"),
            )
            r_missing = [lv for lv in ALL_CEFR_LEVELS if lv not in r_pool]
            r_seeded = await _seeded_pool(
                db,
                language_id=language_id,
                skill=LanguageSkill.reading,
                levels=r_missing,
            )
            r_generated_bank = await _generated_pool(
                db, language_id=language_id, levels=r_missing
            )
            g_pool = await _question_bank_pool(
                db,
                language_id=language_id,
                skill="grammar_vocab",
                levels=ALL_CEFR_LEVELS,
                used_item_ids=_already_used_bank_item_ids(source_state, "grammar_vocab"),
            )
            l_pool = await _question_bank_pool(
                db, language_id=language_id, skill="listening", levels=ALL_CEFR_LEVELS,
                used_item_ids=_already_used_bank_item_ids(source_state, "listening"),
            )
            l_missing = [lv for lv in ALL_CEFR_LEVELS if lv not in l_pool]
            l_seeded = await _seeded_pool(
                db,
                language_id=language_id,
                skill=LanguageSkill.listening,
                levels=l_missing,
            )
            writing_used_ids = _already_used_bank_item_ids(source_state, "writing")
            reviewed_writing_prompt = await _writing_prompt(
                db,
                language_id=language_id,
                level_str=level,
                include_generic=False,
                used_item_ids=writing_used_ids,
            )
            generic_writing_prompt = reviewed_writing_prompt or await _writing_prompt(
                db,
                language_id=language_id,
                level_str=level,
                include_generic=True,
                used_item_ids=writing_used_ids,
            )
            await db.rollback()

        # External-only preparation.  The database session above is closed before reaching here.
        start_level = level if level in ALL_CEFR_LEVELS else "B1"
        missing = [lv for lv in ALL_CEFR_LEVELS if lv not in r_pool]
        try:
            generated_reading = (
                await ai_engine.generate_comprehension_set(skill="reading", levels=missing)
                if missing
                else None
            )
        except Exception:
            generated_reading = None
        for item in (generated_reading or {}).get("items", []):
            r_pool[item["level"]] = {
                "passage": item["text"],
                "situation": "",
                "question": item["question"],
                "options": item["options"],
                "correct_index": item["correct_index"],
                "level": item["level"],
            }
        for fallback_pool in (r_seeded, r_generated_bank):
            for fallback_level, item in fallback_pool.items():
                r_pool.setdefault(fallback_level, item)
        reading_section = _new_adaptive_section(r_pool, start_level)
        grammar_vocab_section = _new_adaptive_section(g_pool, start_level)

        missing = [lv for lv in ALL_CEFR_LEVELS if lv not in l_pool]
        try:
            generated_listening = (
                await ai_engine.generate_comprehension_set(skill="listening", levels=missing)
                if missing
                else None
            )
        except Exception:
            generated_listening = None
        for item in (generated_listening or {}).get("items", []):
            l_pool[item["level"]] = {
                "audio_text": item["text"],
                "situation": item["situation"],
                "question": item["question"],
                "options": item["options"],
                "correct_index": item["correct_index"],
                "level": item["level"],
            }
        for fallback_level, item in l_seeded.items():
            l_pool.setdefault(fallback_level, item)
        # Every TTS call runs after the DB context closed.  Missing audio removes that rung instead
        # of exposing its transcript or fabricating listening evidence.
        for listening_level, item in list(l_pool.items()):
            audio_url, _audio_text, _created = await _materialize_listening_audio(None, item)
            if not audio_url:
                l_pool.pop(listening_level, None)
        listening_section = _new_adaptive_section(l_pool, start_level)

        writing_prompt = reviewed_writing_prompt
        if not writing_prompt:
            try:
                writing_prompt = await ai_engine.generate_writing_prompt(level=level)
            except Exception:
                writing_prompt = None
        writing_prompt = writing_prompt or generic_writing_prompt
        writing_section = {
            "prompt": writing_prompt or "",
            "prompt_token": _new_exam_token() if writing_prompt else "",
            "min_words": WRITING_MIN_WORDS,
            "response": None,
            "ready": bool(writing_prompt),
            "done": False,
            "evidence_status": (
                "missing_student_response" if writing_prompt else "content_unavailable"
            ),
        }
        prepared = {
            "reading": reading_section,
            "listening": listening_section,
            "grammar_vocab": grammar_vocab_section,
            "writing": writing_section,
        }
        await _merge_prepared_content(
            session_id=session_id,
            prep_token=prep_token,
            source_revision=source_revision,
            prepared=prepared,
        )
    except Exception as exc:
        _cleanup_exam_audio({"listening": {"pool": l_pool}})
        logger.warning(
            "Placement content preparation failed session_id=%s error_type=%s",
            session_id,
            type(exc).__name__,
        )
        if prep_token:
            await _mark_content_prep_unavailable(
                session_id=session_id,
                prep_token=prep_token,
                error_code="content_preparation_failed",
            )


async def _merge_prepared_content(
    *,
    session_id: str,
    prep_token: str,
    source_revision: int,
    prepared: dict[str, dict],
) -> bool:
    """Merge only prepared sections into the latest row under a short PostgreSQL lock."""
    async with AsyncSessionLocal() as merge_db:
        sess = (
            await merge_db.execute(
                select(LanguageExamSession)
                .where(LanguageExamSession.id == session_id)
                .with_for_update()
            )
        ).scalar_one_or_none()
        if not sess or sess.status in {"abandoned", "completed", "failed", "evaluating"}:
            _cleanup_exam_audio(prepared)
            return False

        latest = copy.deepcopy(sess.exam_state or {})
        if str(latest.get("content_prep_token") or "") != prep_token:
            _cleanup_exam_audio(prepared)
            return False

        merged_any = False
        for section, value in prepared.items():
            current = latest.get(section, {})
            already_answered = bool(current.get("asked")) or bool(current.get("response")) or bool(current.get("done"))
            if already_answered or current.get("ready") is True:
                if section == "listening":
                    _cleanup_exam_audio({"listening": value})
                continue
            latest[section] = value
            merged_any = True

        if not merged_any:
            _cleanup_exam_audio(prepared)
            return False

        latest["content_prep_status"] = (
            "completed"
            if all(latest.get(section, {}).get("ready") for section in PREPARED_SECTIONS)
            else "content_unavailable"
        )
        latest["content_prepared_from_revision"] = source_revision
        latest["content_prepared_at"] = datetime.now(timezone.utc).isoformat()
        _bump_state_revision(latest)
        sess.exam_state = latest
        flag_modified(sess, "exam_state")
        await merge_db.commit()
        return True


async def _writing_prompt(
    db: AsyncSession,
    *,
    language_id: int,
    level_str: str,
    include_generic: bool = True,
    used_item_ids: set[int] | None = None,
) -> str | None:
    """Pull a reviewed/seeded writing prompt near the level; optionally fall back to generic."""
    try:
        lvl = LanguageLevel(level_str)
    except ValueError:
        lvl = LanguageLevel.A2
    for row in await select_placement_bank_items(
        db,
        language_id=language_id,
        skill="writing_prompt",
        level=lvl,
        count=1,
        used_item_ids=used_item_ids,
    ):
        item = bank_item_to_exam_item(row)
        prompt = str(item.get("question") or "").strip()
        if prompt:
            return prompt
    q = (
        select(LanguageContentItem)
        .where(
            LanguageContentItem.language_id == language_id,
            LanguageContentItem.skill == LanguageSkill.writing,
            LanguageContentItem.content_type == "writing_prompt",
            LanguageContentItem.level == lvl,
            LanguageContentItem.is_published.is_(True),
        )
        .order_by(func.random())
        .limit(1)
    )
    row = (await db.execute(q)).scalar_one_or_none()
    if row:
        body = row.body_json or {}
        prompt = body.get("prompt") or body.get("text") or row.title
        if prompt:
            return str(prompt)
    if not include_generic:
        return None
    return (
        "Write a short message (at least 40 words) describing a memorable day you had recently. "
        "Explain what happened, who you were with, and how you felt."
    )


_SPEAKING_BANK_SCENARIO = {
    "scenario": "AI placement speaking assessment",
    "ai_persona": "an English placement examiner",
    "student_role": "a test-taker",
    "setting": "a spoken placement exam",
}


_SPEAKING_LEVEL_ORDER = [
    LanguageLevel.A1,
    LanguageLevel.A2,
    LanguageLevel.B1,
    LanguageLevel.B2,
    LanguageLevel.C1,
    LanguageLevel.C2,
]


def _adjacent_speaking_levels(level: LanguageLevel) -> list[LanguageLevel]:
    """CEFR levels exactly one band above/below the given level (closer direction first: up,
    then down), e.g. B1 -> [B2, A1]; A1 (no lower neighbor) -> [A2]; C2 (no higher neighbor) ->
    [C1]. Used only by _speaking_bank_prompt's diversity fallback -- never for scoring/level
    estimation, and never for any other bank skill."""
    try:
        rank = _SPEAKING_LEVEL_ORDER.index(level)
    except ValueError:
        return []
    neighbors = []
    if rank + 1 < len(_SPEAKING_LEVEL_ORDER):
        neighbors.append(_SPEAKING_LEVEL_ORDER[rank + 1])
    if rank - 1 >= 0:
        neighbors.append(_SPEAKING_LEVEL_ORDER[rank - 1])
    return neighbors


async def _speaking_bank_prompt(
    db: AsyncSession,
    *,
    language_id: int,
    level_str: str,
    used_item_ids: set[int] | None = None,
    used_subskills: set[str] | None = None,
) -> dict | None:
    """Pull one verified, unused, MVP-marked speaking_prompt bank item at the target level, or
    None if the bank has nothing usable (caller falls back to live scenario/question generation)
    -- mirrors _writing_prompt's exact-level-then-fallback pattern.

    require_mvp_marker=True restricts selection to the curated MVP bank
    (body_json.review_status="mvp_approved_pending_full_review"), excluding older/legacy
    speaking_prompt rows seeded by the generic seed_placement_question_bank.py script that
    predate it -- those legacy rows are untouched (not deleted/deactivated), just never
    selected here.

    used_subskills, if given, is a soft diversity preference applied in priority order (never a
    hard requirement -- a thin bank can never fail to produce a prompt just because every
    remaining item shares an already-seen subskill):
      1. Target level, preferring an item whose subskill/task_type hasn't appeared this session.
      2. An adjacent CEFR level (+/-1 band), still preferring an unused subskill -- covers levels
         that today have exactly one subskill of their own (e.g. A1 = self_intro only, A2 =
         routine_description only), where a second turn at the same level would otherwise always
         repeat it even though a neighboring level has something fresh.
      3. Target level again, unused bank_item_id only -- subskill may repeat.
      4. None -- caller falls back to live AI generation."""
    try:
        lvl = LanguageLevel(level_str)
    except ValueError:
        lvl = LanguageLevel.A2

    async def _at_level(level: LanguageLevel, *, exclude_subskills: set[str] | None) -> dict | None:
        for row in await select_placement_bank_items(
            db,
            language_id=language_id,
            skill="speaking_prompt",
            level=level,
            count=1,
            used_item_ids=used_item_ids,
            require_mvp_marker=True,
            exclude_subskills=exclude_subskills,
        ):
            item = bank_item_to_exam_item(row)
            if str(item.get("question") or "").strip():
                return item
        return None

    if used_subskills:
        item = await _at_level(lvl, exclude_subskills=used_subskills)
        if item is not None:
            return item
        for neighbor in _adjacent_speaking_levels(lvl):
            item = await _at_level(neighbor, exclude_subskills=used_subskills)
            if item is not None:
                return item

    return await _at_level(lvl, exclude_subskills=None)


def _speaking_bank_question_text(item: dict) -> str:
    situation = str(item.get("situation") or "").strip()
    question = str(item.get("question") or "").strip()
    return f"{situation} {question}".strip() if situation else question


def _speaking_scenario_from_bank_item(item: dict) -> dict:
    """A generic, honest scenario descriptor for bank-sourced speaking turns -- curated items are
    independent semi-structured prompts, not a continuous roleplay, so persona/setting stay
    fixed for the session rather than switching per item (MVP simplification)."""
    return {**_SPEAKING_BANK_SCENARIO, "opening_question": _speaking_bank_question_text(item)}


def _already_used_speaking_bank_item_ids(state: dict, section: str) -> set[int]:
    """Bank item ids already asked in this session's speaking-like section. Mirrors
    _already_used_bank_item_ids (P1.1) for MCQ sections, but speaking's turn history lives under
    "results", not "asked"."""
    results = state.get(section, {}).get("results", []) or []
    return {int(r["bank_item_id"]) for r in results if r.get("bank_item_id")}


def _already_used_speaking_subskills(state: dict, section: str) -> set[str]:
    """Subskill/task_type values already asked in this session's speaking-like section -- used
    only as _speaking_bank_prompt's soft diversity preference (never a hard exclusion), so
    back-to-back turns avoid repeating the same task type (e.g. self_intro, self_intro) when a
    fresher one is available at the target level."""
    results = state.get(section, {}).get("results", []) or []
    return {str(r["bank_item_subskill"]) for r in results if r.get("bank_item_subskill")}


# ---------------------------------------------------------------------------------------
# state -> output contract
# ---------------------------------------------------------------------------------------

def _current_section(state: dict) -> str | None:
    cursor = state.get("cursor", 0)
    sections = state.get("sections", SECTIONS)
    if cursor >= len(sections):
        return None
    return sections[cursor]


async def _build_state_out(
    db: AsyncSession,
    sess: LanguageExamSession,
    *,
    last_feedback: SpeakingTurnFeedbackOut | None = None,
    resumed: bool = False,
) -> ExamStateOut:
    """Render a state snapshot without locks or external AI/STT/TTS work."""
    _ = db
    state = sess.exam_state or {}
    sections = state.get("sections", SECTIONS)
    cursor = state.get("cursor", 0)
    revision = _state_revision(state)

    if sess.status in ("evaluating", "completed", "failed") or cursor >= len(sections):
        phase = sess.status if sess.status in ("completed", "failed") else "evaluating"
        evaluation = dict(state.get("evaluation") or {})
        evaluation_status = str(
            evaluation.get("evaluation_status") or evaluation.get("status") or "retry_required"
        )
        return ExamStateOut(
            session_id=sess.id, state_revision=revision, phase=phase, section_index=len(sections),
            section_total=len(sections), sections=sections, resumed=resumed,
            evidence_status="completed" if sess.status == "completed" else evaluation_status,
            error_code=evaluation.get("error_code"),
            error_message=evaluation.get("error_message"),
        )

    section = sections[cursor]

    # Reading/listening/writing content is generated in the background; until it's ready, tell the
    # frontend to show a loader and poll. (Older sessions without the flag are treated as ready.)
    if section in PREPARED_SECTIONS and not state.get(section, {}).get("ready", True):
        unavailable = (
            state.get(section, {}).get("evidence_status") == "content_unavailable"
            or state.get("content_prep_status") == "content_unavailable"
        )
        return ExamStateOut(
            session_id=sess.id,
            state_revision=revision,
            phase="content_unavailable" if unavailable else "preparing",
            section_index=cursor,
            section_total=len(sections), sections=sections, resumed=resumed,
            evidence_status="content_unavailable" if unavailable else "retry_required",
            error_code="content_unavailable" if unavailable else None,
            error_message=(
                "Required placement content is temporarily unavailable. Please retry."
                if unavailable
                else None
            ),
        )

    out = ExamStateOut(
        session_id=sess.id, state_revision=revision, phase=section, section_index=cursor, section_total=len(sections),
        sections=sections, last_feedback=last_feedback, resumed=resumed,
        evidence_status=str(state.get(section, {}).get("evidence_status") or "missing_student_response"),
    )

    if section in SPEAKING_LIKE:
        sp = state[section]
        scenario = state.get("speaking", {}).get("scenario", {})
        title = "Spoken interview" if section == "interview" else scenario.get("scenario", "Role-play")
        out.speaking = SpeakingPromptOut(
            scenario_title=title,
            setting="" if section == "interview" else scenario.get("setting", ""),
            examiner_message=sp.get("pending_question", ""),
            turn=sp.get("turn", 1),
            total_turns=sp.get("total_turns", INTERVIEW_TURNS if section == "interview" else SPEAKING_TURNS),
            turn_token=str(sp.get("turn_token") or ""),
        )
        out.turn_token = out.speaking.turn_token
    elif section in MCQ_SECTIONS:
        sec = state[section]
        item = sec.get("pool", {}).get(sec.get("current_level"))
        if item and not sec.get("done"):
            audio_url = None
            passage = item.get("passage") or None if section == "reading" else None
            situation = item.get("situation") or None if section == "listening" else None
            instructions = "Choose the best answer."
            if section == "listening":
                instructions = "Listen to the clip, then answer."
                audio_url = str(item.get("audio_url") or "") or None
                if not audio_url:
                    out.phase = "content_unavailable"
                    out.evidence_status = "content_unavailable"
                    out.error_code = "listening_audio_unavailable"
                    out.error_message = "Listening audio is temporarily unavailable. Please retry."
                    return out
            elif section == "reading":
                instructions = "Read the passage, then answer."
            elif section == "grammar_vocab":
                instructions = "Choose the most accurate English option."
            out.mcq = McqPromptOut(
                instructions=instructions,
                passage=passage,
                audio_url=audio_url,
                situation=situation,
                question=item.get("question", ""),
                options=item.get("options", []),
                item_index=len(sec.get("asked", [])),
                item_total=sec.get("max_steps", ADAPTIVE_MAX_STEPS),
                question_token=str(item.get("question_token") or ""),
            )
            out.question_token = out.mcq.question_token
    elif section == "writing":
        wr = state["writing"]
        out.writing = WritingPromptOut(
            prompt=wr.get("prompt", ""),
            min_words=wr.get("min_words", WRITING_MIN_WORDS),
            prompt_token=str(wr.get("prompt_token") or ""),
        )
        out.prompt_token = out.writing.prompt_token

    return out


async def _resolve_listening_audio(db: AsyncSession | None, item: dict) -> str | None:
    """Return only audio that is tied to the same transcript as the question.

    If the audio cannot be tied to this item, the caller must generate it server-side or fail closed;
    the private transcript is never sent to the browser.
    """

    audio_url = item.get("audio_url")
    if _is_usable_audio_url(audio_url):
        return str(audio_url)

    content_item_id = item.get("content_id")
    if not content_item_id or db is None:
        return None

    content = await db.get(LanguageContentItem, content_item_id)
    body = content.body_json if content else {}
    body_audio_url = (body or {}).get("audio_url")
    if _listening_text_from_body(body) and _is_usable_audio_url(body_audio_url):
        return str(body_audio_url)
    return None


async def _resolve_listening_audio_text(db: AsyncSession | None, item: dict) -> str | None:
    text = str(item.get("audio_text") or "").strip()
    if text:
        return text

    content_item_id = item.get("content_id")
    if not content_item_id or db is None:
        return None
    content = await db.get(LanguageContentItem, content_item_id)
    body = content.body_json if content else {}
    text = _listening_text_from_body(body)
    return text or None


async def _materialize_listening_audio(
    db: AsyncSession | None, item: dict
) -> tuple[str | None, str | None, bool]:
    """Ensure a listening item has a real audio URL generated from its own transcript."""

    audio_url = await _resolve_listening_audio(db, item)
    audio_text = await _resolve_listening_audio_text(db, item)
    if audio_url:
        return audio_url, audio_text, False
    if not audio_text:
        return None, None, False

    generated_url = None
    try:
        generated_url = await synthesize_exam_audio(audio_text)
    except Exception as exc:  # pragma: no cover - model/runtime variance
        logger.warning("Placement listening TTS failed error_type=%s", type(exc).__name__)

    if _is_usable_audio_url(generated_url):
        item["audio_url"] = str(generated_url)
        item["audio_text"] = audio_text
        return str(generated_url), audio_text, True

    item["audio_text"] = audio_text
    return None, audio_text, False


def _advance_if_section_done(state: dict) -> None:
    """Move the cursor forward while the current section is marked done."""
    sections = state.get("sections", SECTIONS)
    while state.get("cursor", 0) < len(sections):
        section = sections[state["cursor"]]
        if state.get(section, {}).get("done"):
            state["cursor"] += 1
        else:
            break


_REQUEST_RECEIPT_LIMIT = 100


def _normalise_writing_text(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text or "").split())


def canonical_payload_hash(*, kind: str, payload: dict) -> str:
    """Hash a canonical operation payload for durable idempotency receipts."""
    encoded = json.dumps(
        {"kind": kind, **payload},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _request_receipt(
    state: dict,
    *,
    kind: str,
    request_id: str,
    payload_hash: str,
) -> dict | None:
    """Return the completed receipt, or reject reuse of an id with different input."""
    for receipt in state.get("request_receipts", []):
        # ``id`` is accepted only to read receipts produced by early phase-zero builds.
        stored_request_id = receipt.get("request_id") or receipt.get("id")
        if stored_request_id != request_id:
            continue
        if receipt.get("kind") == kind and secrets.compare_digest(
            str(receipt.get("payload_hash") or ""), payload_hash
        ):
            return receipt
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "idempotency_conflict",
                "message": "request_id was already used with a different payload.",
                "current_state_revision": _state_revision(state),
            },
        )
    return None


def _record_request(
    state: dict,
    *,
    kind: str,
    request_id: str,
    payload_hash: str,
    request_revision: int,
    token: str,
    result_reference: str,
) -> None:
    receipts = list(state.get("request_receipts", []))
    receipts.append(
        {
            "request_id": request_id,
            "kind": kind,
            "payload_hash": payload_hash,
            "state_revision": request_revision,
            "token": token,
            "result_reference": result_reference,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    state["request_receipts"] = receipts[-_REQUEST_RECEIPT_LIMIT:]


def _require_current_state(
    state: dict,
    *,
    supplied_revision: int,
    supplied_token: str,
    expected_token: str,
) -> None:
    _require_state_revision(state, supplied_revision=supplied_revision)
    current_revision = _state_revision(state)
    if not expected_token or not secrets.compare_digest(
        str(supplied_token), str(expected_token)
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "stale_exam_state",
                "message": "The exam moved forward. Refresh the current question before retrying.",
                "current_state_revision": current_revision,
            },
        )


def _require_state_revision(state: dict, *, supplied_revision: int) -> None:
    current_revision = _state_revision(state)
    if supplied_revision != current_revision:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "stale_exam_state",
                "message": "The exam moved forward. Refresh the current question before retrying.",
                "current_state_revision": current_revision,
            },
        )


def _audio_hash_already_used(state: dict, audio_sha256: str) -> bool:
    return any(
        str(result.get("audio_sha256") or "") == audio_sha256
        for spoken_section in SPEAKING_LIKE
        for result in state.get(spoken_section, {}).get("results", [])
    )


def exam_evidence_statuses(state: dict) -> dict[str, str]:
    """Classify evidence without blaming the student for missing server-side content."""
    statuses: dict[str, str] = {}
    for section in ("listening", "reading", "grammar_vocab"):
        section_state = state.get(section, {})
        declared = str(section_state.get("evidence_status") or "")
        if declared in {"content_unavailable", "retry_required", "unassessed"}:
            statuses[section] = declared
            continue
        if not section_state.get("ready", True) or not section_state.get("pool"):
            statuses[section] = "content_unavailable"
            continue
        asked = section_state.get("asked") or []
        valid = [
            answer
            for answer in asked
            if isinstance(answer.get("correct"), bool)
            and isinstance(answer.get("chosen_index"), int)
            and bool(answer.get("level"))
        ]
        if not valid or section_state.get("done") is not True:
            statuses[section] = "missing_student_response"
        else:
            statuses[section] = "completed"

    writing = state.get("writing", {})
    min_words = max(WRITING_MIN_WORDS, int(writing.get("min_words") or WRITING_MIN_WORDS))
    declared = str(writing.get("evidence_status") or "")
    if declared in {"content_unavailable", "retry_required", "unassessed"}:
        statuses["writing"] = declared
    elif not writing.get("ready", True) or not str(writing.get("prompt") or "").strip():
        statuses["writing"] = "content_unavailable"
    elif writing.get("done") is not True or len(str(writing.get("response") or "").split()) < min_words:
        statuses["writing"] = "missing_student_response"
    else:
        statuses["writing"] = "completed"

    # Sections-driven: only require evidence for a spoken phase if this session's own persisted
    # "sections" list actually includes it. New sessions have no "interview" entry and must not
    # be blocked on it; old sessions that still have "interview" must keep requiring it.
    session_sections = state.get("sections") or SECTIONS
    spoken_defaults = [("speaking", SPEAKING_TURNS), ("interview", INTERVIEW_TURNS)]
    for section, default_turns in [(s, t) for s, t in spoken_defaults if s in session_sections]:
        spoken = state.get(section, {})
        declared = str(spoken.get("evidence_status") or "")
        if declared in {"content_unavailable", "retry_required", "unassessed"}:
            statuses[section] = declared
            continue
        required = max(1, int(spoken.get("total_turns") or default_turns))
        results = spoken.get("results") or []
        valid = [
            result
            for result in results
            if str(result.get("transcription") or "").strip()
            and str(result.get("audio_sha256") or "").strip()
            and str(result.get("question") or "").strip()
        ]
        distinct_audio = {str(result.get("audio_sha256")) for result in valid}
        if spoken.get("done") is not True or len(valid) < required or len(distinct_audio) < required:
            statuses[section] = "missing_student_response"
        else:
            statuses[section] = "completed"
    return statuses


def missing_exam_evidence(state: dict) -> dict[str, str]:
    """Return incomplete sections with a stable, report-safe reason."""
    messages = {
        "missing_student_response": "A required student response is missing.",
        "content_unavailable": "Required exam content is temporarily unavailable.",
        "scorer_unavailable": "The authoritative scorer is temporarily unavailable.",
        "retry_required": "This section must be retried.",
        "unassessed": "This section has not been authoritatively assessed.",
    }
    return {
        section: messages[section_status]
        for section, section_status in exam_evidence_statuses(state).items()
        if section_status != "completed"
    }


def _ensure_exam_evidence_complete(state: dict) -> None:
    missing = missing_exam_evidence(state)
    if missing:
        statuses = exam_evidence_statuses(state)
        technical = {
            section: section_status
            for section, section_status in statuses.items()
            if section_status in {"content_unavailable", "scorer_unavailable", "retry_required", "unassessed"}
        }
        if technical:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "exam_evidence_unavailable",
                    "message": "Required exam evidence is temporarily unavailable. Please retry.",
                    "section_statuses": statuses,
                    "retry_sections": list(technical),
                },
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "incomplete_exam",
                "message": "The placement test is missing required evidence.",
                "missing_sections": list(missing),
                "missing_evidence": missing,
                "section_statuses": statuses,
            },
        )


def _provisional_from_phase1(state: dict) -> tuple[CEFRLevel, str]:
    """Deterministic Phase-1 rollup: provisional level + the most uncertain/weak area."""
    levels: list[CEFRLevel] = []
    sp_results = state.get("speaking", {}).get("results", [])
    sp_levels = []
    for r in sp_results:
        try:
            sp_levels.append(CEFRLevel(r.get("estimated_level")))
        except (ValueError, TypeError):
            pass
    speaking_level = overall_level(sp_levels) if sp_levels else None

    def _comp_level(section: str) -> CEFRLevel | None:
        asked = state.get(section, {}).get("asked", [])
        if not asked:
            return None
        level, _ = adaptive_result(asked)
        return level

    reading_level = _comp_level("reading")
    listening_level = _comp_level("listening")
    grammar_vocab_level = _comp_level("grammar_vocab")
    for lv in (speaking_level, reading_level, listening_level, grammar_vocab_level):
        if lv is not None:
            levels.append(lv)
    provisional = overall_level(levels) if levels else CEFRLevel.A2

    # The "uncertain band" = where the skills disagree most; weak area = lowest skill.
    named = [
        ("speaking", speaking_level),
        ("reading", reading_level),
        ("listening", listening_level),
        ("grammar/vocabulary", grammar_vocab_level),
    ]
    present = [(n, lv) for n, lv in named if lv is not None]
    weak = min(present, key=lambda x: cefr_rank(x[1]))[0] if present else "speaking"
    nxt = cefr_from_rank(cefr_rank(provisional) + 1)
    priming = (
        f"Provisional level ~{provisional.value}; weakest area so far is {weak}. "
        f"Probe the {provisional.value}/{nxt.value} boundary and pressure-test {weak}."
    )
    return provisional, priming


async def _ensure_interview_ready(state: dict) -> None:
    """Lazily build the Phase-2 priming + opening question when entering the interview section."""
    if _current_section(state) != "interview":
        return
    iv = state.setdefault("interview", {})
    if iv.get("pending_question"):
        return
    _, priming = _provisional_from_phase1(state)
    iv["priming"] = priming
    iv["total_turns"] = iv.get("total_turns", INTERVIEW_TURNS)
    iv["turn"] = iv.get("turn", 1)
    iv.setdefault("results", [])
    iv["pending_question"] = await ai_engine.interview_opening(
        priming=priming,
        scenario=state.get("speaking", {}).get("scenario", {}),
        learner_grade=state.get("learner_grade"),
    )
    iv["turn_token"] = _new_exam_token()
    iv["evidence_status"] = "missing_student_response"


# ---------------------------------------------------------------------------------------
# background final evaluation
# ---------------------------------------------------------------------------------------

# Realistic study time to climb one CEFR band (higher bands take longer); C2 = already top.
_WEEKS_TO_NEXT = {"A1": 10, "A2": 12, "B1": 16, "B2": 20, "C1": 24, "C2": 0}


def _weeks_to_next_level(level: CEFRLevel) -> int:
    return _WEEKS_TO_NEXT.get(level.value, 14)


def _parse_utc(value: object) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def evaluation_lease_expired(state: dict, *, now: datetime | None = None) -> bool:
    evaluation = dict(state.get("evaluation") or {})
    current_status = str(evaluation.get("evaluation_status") or evaluation.get("status") or "")
    if current_status != "running":
        return True
    expiry = _parse_utc(evaluation.get("evaluation_lease_expires_at") or evaluation.get("lease_expires_at"))
    return expiry is None or expiry <= (now or datetime.now(timezone.utc))


def _evaluation_should_run(state: dict) -> bool:
    evaluation = dict(state.get("evaluation") or {})
    current_status = str(evaluation.get("evaluation_status") or evaluation.get("status") or "pending")
    return current_status in {"pending", "retry_required", "scorer_unavailable", "failed"} or (
        current_status == "running" and evaluation_lease_expired(state)
    )


async def _claim_evaluation_lease(session_id: str) -> tuple[str, dict, int, int] | None:
    """Atomically own an evaluation attempt, returning an immutable evidence snapshot."""
    now = datetime.now(timezone.utc)
    owner = uuid.uuid4().hex
    async with AsyncSessionLocal() as claim_db:
        sess = (
            await claim_db.execute(
                select(LanguageExamSession)
                .where(LanguageExamSession.id == session_id)
                .with_for_update()
            )
        ).scalar_one_or_none()
        if not sess or sess.status != "evaluating" or sess.is_completed:
            return None
        if not check("placement_evaluation", f"{sess.student_id}:{session_id}"):
            return None
        state = copy.deepcopy(sess.exam_state or {})
        _ensure_exam_evidence_complete(state)
        evaluation = dict(state.get("evaluation") or {})
        current_status = str(evaluation.get("evaluation_status") or evaluation.get("status") or "pending")
        if current_status == "running" and not evaluation_lease_expired(state, now=now):
            return None
        evaluation.update(
            {
                "evaluation_status": "running",
                "evaluation_started_at": now.isoformat(),
                "evaluation_lease_expires_at": (
                    now + timedelta(seconds=EVALUATION_LEASE_SECONDS)
                ).isoformat(),
                "evaluation_attempt": int(
                    evaluation.get("evaluation_attempt") or evaluation.get("attempt") or 0
                )
                + 1,
                "evaluation_owner": owner,
            }
        )
        for old_key in ("status", "started_at", "attempt", "lease_expires_at"):
            evaluation.pop(old_key, None)
        state["evaluation"] = evaluation
        _bump_state_revision(state)
        sess.exam_state = state
        flag_modified(sess, "exam_state")
        await claim_db.commit()
        return owner, copy.deepcopy(state), sess.student_id, sess.language_id


async def _renew_evaluation_lease(session_id: str, owner: str) -> bool:
    """Extend a live owner's lease in a short, owner-fenced transaction."""
    async with AsyncSessionLocal() as lease_db:
        sess = (
            await lease_db.execute(
                select(LanguageExamSession)
                .where(LanguageExamSession.id == session_id)
                .with_for_update()
            )
        ).scalar_one_or_none()
        if not sess or sess.status != "evaluating" or sess.is_completed:
            return False
        state = copy.deepcopy(sess.exam_state or {})
        evaluation = dict(state.get("evaluation") or {})
        if (
            str(evaluation.get("evaluation_status") or "") != "running"
            or not secrets.compare_digest(str(evaluation.get("evaluation_owner") or ""), owner)
        ):
            return False
        evaluation["evaluation_lease_expires_at"] = (
            datetime.now(timezone.utc) + timedelta(seconds=EVALUATION_LEASE_SECONDS)
        ).isoformat()
        state["evaluation"] = evaluation
        _bump_state_revision(state)
        sess.exam_state = state
        flag_modified(sess, "exam_state")
        await lease_db.commit()
        return True


async def _evaluation_lease_heartbeat(
    session_id: str,
    owner: str,
    stop: asyncio.Event,
) -> None:
    """Keep a healthy long-running scorer from being mistaken for a stale worker."""
    interval = max(0.1, min(30.0, EVALUATION_LEASE_SECONDS / 3.0))
    while True:
        try:
            await asyncio.wait_for(stop.wait(), timeout=interval)
            return
        except asyncio.TimeoutError:
            try:
                if not await _renew_evaluation_lease(session_id, owner):
                    return
            except Exception as exc:  # A lost heartbeat leaves the ordinary expiry recovery intact.
                logger.warning(
                    "Evaluation lease heartbeat failed session_id=%s error_type=%s",
                    session_id,
                    type(exc).__name__,
                )
                return


async def _run_evaluation(session_id: str) -> None:
    """Own and heartbeat one evaluation; a live worker cannot be duplicated after lease expiry."""
    claim = await _claim_evaluation_lease(session_id)
    if claim is None:
        return
    owner = claim[0]
    stop_heartbeat = asyncio.Event()
    heartbeat = asyncio.create_task(
        _evaluation_lease_heartbeat(session_id, owner, stop_heartbeat)
    )
    try:
        await _run_claimed_evaluation(session_id, claim)
    finally:
        stop_heartbeat.set()
        await heartbeat


async def _run_claimed_evaluation(
    session_id: str,
    claim: tuple[str, dict, int, int],
) -> None:
    """Fuse the immutable claimed evidence, then owner-fence the atomic DB projection."""
    evaluation_owner, state, student_id, language_id = claim
    async with AsyncSessionLocal() as db:
        try:
            now = datetime.now(timezone.utc)
            # --- Shared: per-turn evidence block + effective-level guess.
            def _block(results: list[dict]) -> str:
                return "\n".join(
                    "<spoken_turn>\n"
                    f"<question>{r.get('question', '')}</question>\n"
                    f"<server_transcript>{r.get('transcription', '')}</server_transcript>\n"
                    f"<audio_duration_seconds>{r.get('audio_duration_seconds', '')}</audio_duration_seconds>\n"
                    "</spoken_turn>"
                    for r in results
                ) or "(none)"

            guess = await _effective_level(db, student_id=student_id, language_id=language_id)
            # Release the read transaction before any scorer call; no DB connection or row lock is
            # held while external AI work is in flight.
            await db.rollback()

            # --- Speaking: independent 4-criteria rubric over Phase-1 + Phase-2 turns.
            ph1_results = state.get("speaking", {}).get("results", [])
            ph2_results = state.get("interview", {}).get("results", [])
            sp_results = ph1_results + ph2_results
            # "interview" was a deliberate, intentional Phase-2 addition for sessions that have it
            # in their own persisted sections — for those, live_available still means "did the
            # interview actually produce results" (unchanged). For sessions with no "interview"
            # section at all (the new, no-interview design), there is no Phase 2 to be
            # "unavailable" — Phase-1 speaking evidence being complete is what "available" means.
            if "interview" in (state.get("sections") or SECTIONS):
                live_available = bool(ph2_results)
            else:
                live_available = len(ph1_results) >= SPEAKING_TURNS
            sp_evidence = build_verified_speaking_evidence(ph1_results, ph2_results)
            sp_detected: list = []
            if sp_results:
                sp_grade = await ai_engine.grade_speaking(evidence=sp_evidence, effective_level=guess)
                speaking_level, speaking_score = sp_grade.level, sp_grade.score
                speaking_breakdown = {
                    "fluency": sp_grade.fluency, "lexical": sp_grade.lexical,
                    "grammar": sp_grade.grammar,
                }
                sp_detected = list(sp_grade.detected_errors)
            else:
                raise RuntimeError("Verified speaking evidence is unavailable")

            # --- Reading / Listening: adaptive (staircase) result.
            r_asked = state.get("reading", {}).get("asked", [])
            l_asked = state.get("listening", {}).get("asked", [])
            g_asked = state.get("grammar_vocab", {}).get("asked", [])
            reading_level, reading_pct = adaptive_result(r_asked)
            listening_level, listening_pct = adaptive_result(l_asked)
            grammar_vocab_level, grammar_vocab_pct = adaptive_result(g_asked)
            r_correct, r_total = sum(1 for a in r_asked if a.get("correct")), len(r_asked)
            l_correct, l_total = sum(1 for a in l_asked if a.get("correct")), len(l_asked)
            g_correct, g_total = sum(1 for a in g_asked if a.get("correct")), len(g_asked)

            # --- Writing: AI grade.
            wr = state.get("writing", {})
            grade = await ai_engine.grade_writing(
                prompt_text=wr.get("prompt", ""), answer=wr.get("response", ""), effective_level=guess
            )
            writing_level, writing_score = grade.level, grade.score

            overall = overall_level([reading_level, listening_level, writing_level, speaking_level])

            # --- Cross-phase triangulation: do the spoken and written signals agree?
            #     Spoken = speaking interview; written-anchor = reading/listening/writing plus grammar/vocab.
            spoken_rank = cefr_rank(speaking_level)
            written_anchor_levels = [reading_level, listening_level, writing_level]
            if g_asked:
                written_anchor_levels.append(grammar_vocab_level)
            written_rank = cefr_rank(overall_level(written_anchor_levels))
            gap = spoken_rank - written_rank
            if not live_available:
                consistency = "live_phase_unavailable"
                confidence = 0.55
            elif abs(gap) <= 0:
                consistency = "consistent"
                confidence = 0.92
            elif abs(gap) == 1:
                consistency = "consistent"
                confidence = 0.8
            else:
                consistency = "speaking_stronger" if gap > 0 else "writing_stronger"
                confidence = 0.6
            # No acoustic scorer is present. Make that limitation visible and reduce confidence;
            # pronunciation is never inserted as a fabricated numeric criterion.
            confidence = min(confidence * 0.85, 0.78)

            # --- Narrative from all evidence. Pronunciation is deliberately unassessed because
            #     final grading receives verified transcripts, not the raw audio signal.
            grammar_evidence = (
                f"GRAMMAR/VOCAB: {g_correct}/{g_total} correct -> {grammar_vocab_level.value}\n\n"
                if g_asked
                else "GRAMMAR/VOCAB: not measured\n\n"
            )
            evidence = (
                "Weighting: verified speech transcripts support spoken coherence, grammar and "
                "vocabulary; pronunciation is unassessed. Written items anchor grammar and vocabulary.\n\n"
                f"PHASE 1 ΓÇö ROLE-PLAY SPEAKING:\n{_block(ph1_results)}\n\n"
                f"PHASE 2 ΓÇö GUIDED INTERVIEW:\n{_block(ph2_results)}\n\n"
                f"LISTENING: {l_correct}/{l_total} correct -> {listening_level.value}\n"
                f"READING: {r_correct}/{r_total} correct -> {reading_level.value}\n\n"
                f"{grammar_evidence}"
                f"WRITING (level {writing_level.value}, score {writing_score}):\n"
                f"Task: {wr.get('prompt','')}\nAnswer: {wr.get('response','')}\n"
                f"Grader feedback: {grade.feedback}\n\n"
                f"Cross-phase consistency: {consistency}."
            )
            narrative = await ai_engine.build_final_narrative(evidence=evidence)

            # --- Backend-computed guidance: strongest/weakest skill + time to next level.
            skill_levels = {
                "reading": reading_level, "listening": listening_level,
                "writing": writing_level, "speaking": speaking_level,
            }
            strongest = max(skill_levels.items(), key=lambda kv: cefr_rank(kv[1]))[0]
            weakest = min(skill_levels.items(), key=lambda kv: cefr_rank(kv[1]))[0]
            writing_breakdown = {
                "task_achievement": grade.task_achievement,
                "coherence": grade.coherence,
                "lexical": grade.lexical,
                "grammar": grade.grammar,
            }

            detected = list(narrative.detected_errors) + list(grade.detected_errors) + sp_detected
            speaking_turns = [
                {
                    "question": r.get("question", ""),
                    "transcription": r.get("transcription", ""),
                    "grammar_vocab_feedback": r.get("grammar_vocab_feedback", ""),
                    "pronunciation_feedback": "Unassessed: no acoustic pronunciation scorer was used.",
                    "fluency_note": r.get("fluency_note", ""),
                }
                for r in sp_results
                if r.get("transcription")
            ]
            report = MultiSkillReportSchema(
                overall_level=overall,
                reading_level=reading_level,
                listening_level=listening_level,
                writing_level=writing_level,
                speaking_level=speaking_level,
                reading_score_percent=reading_pct,
                listening_score_percent=listening_pct,
                writing_score=writing_score,
                speaking_score=speaking_score,
                grammar_vocab_level=grammar_vocab_level if g_asked else None,
                grammar_vocab_score_percent=grammar_vocab_pct if g_asked else 0.0,
                summary=narrative.summary,
                strengths=narrative.strengths,
                weaknesses=narrative.weaknesses,
                detected_errors=detected[:8],
                recommended_starting_lesson_topic=narrative.recommended_starting_lesson_topic,
                strongest_skill=strongest,
                weakest_skill=weakest,
                recommendations=narrative.recommendations[:3],
                weeks_to_next_level=_weeks_to_next_level(overall),
                writing_breakdown=writing_breakdown,
                speaking_breakdown=speaking_breakdown,
                speaking_turns=speaking_turns,
                confidence=round(confidence, 2),
                cross_phase_consistency=consistency,
                unassessed_components=["speaking.pronunciation"],
            )

            # Reacquire a short lock only after every external scorer has completed. The owner
            # check makes a stale worker harmless if another worker recovered an expired lease.
            await db.rollback()
            sess = (
                await db.execute(
                    select(LanguageExamSession)
                    .where(LanguageExamSession.id == session_id)
                    .with_for_update()
                )
            ).scalar_one_or_none()
            if not sess or sess.status != "evaluating" or sess.is_completed:
                return
            latest_state = copy.deepcopy(sess.exam_state or {})
            latest_evaluation = dict(latest_state.get("evaluation") or {})
            if (
                str(latest_evaluation.get("evaluation_status") or "") != "running"
                or not secrets.compare_digest(
                    str(latest_evaluation.get("evaluation_owner") or ""), evaluation_owner
                )
            ):
                return
            state = latest_state
            now = datetime.now(timezone.utc)
            sess.assessment_report = report.model_dump(mode="json")
            sess.status = "completed"
            sess.is_completed = True
            sess.completed_at = now

            # --- Write authoritative per-skill levels to analytics.
            def _lvl(v: CEFRLevel) -> LanguageLevel:
                try:
                    return LanguageLevel(v.value)
                except ValueError:
                    return LanguageLevel.A1

            analytics = await db.get(
                LanguageAnalytics, {"student_id": sess.student_id, "language_id": sess.language_id}
            )
            if analytics is None:
                analytics = LanguageAnalytics(student_id=sess.student_id, language_id=sess.language_id)
                db.add(analytics)
            # Only persist a level for skills the exam actually measured. A skipped/empty section
            # defaulted to A2 above; claiming a level for an untested skill is misleading. When not
            # measured the column is left unchanged (None on a first exam, prior level on a retake),
            # so the UI shows "ΓÇö" instead of a fabricated A2.
            measured_pairs = [
                ("reading", reading_level, bool(r_asked)),
                ("listening", listening_level, bool(l_asked)),
                ("writing", writing_level, bool((wr.get("response") or "").strip())),
                ("speaking", speaking_level, bool(sp_results)),
            ]
            measured_cefr: list = []
            focus_levels: dict[str, str] = {}
            for skill_key, lvl, was_measured in measured_pairs:
                if was_measured:
                    setattr(analytics, f"{skill_key}_level", _lvl(lvl))
                    measured_cefr.append(lvl)
                    focus_levels[skill_key] = lvl.value
            analytics.overall_level_internal = _lvl(overall_level(measured_cefr) if measured_cefr else overall)
            # Persist the weakest measured skill so the daily plan personalises from day one.
            focus, _strength = primary_focus_and_strength(
                focus_levels
                or {
                    "reading": reading_level.value, "listening": listening_level.value,
                    "writing": writing_level.value, "speaking": speaking_level.value,
                }
            )
            if focus:
                analytics.primary_focus_skill = focus

            # --- Mark placement complete -> unlock the module.
            prof = (
                await db.execute(
                    select(LanguageStudentProfile).where(
                        LanguageStudentProfile.student_id == sess.student_id,
                        LanguageStudentProfile.language_id == sess.language_id,
                    )
                )
            ).scalar_one_or_none()
            if prof is None:
                prof = LanguageStudentProfile(student_id=sess.student_id, language_id=sess.language_id)
                db.add(prof)
            if not prof.placement_completed_at:
                prof.placement_completed_at = now
            prof.last_assessment_date = now
            prof.next_allowed_retake_date = next_allowed_retake_at(now)
            prof.onboarding_step = LanguageOnboardingStep.dashboard

            # Feed the exam's detected errors into Error Intelligence (same bank as conversation),
            # so recurring mistakes surface across BOTH features (best-effort).
            try:
                from app.services.language_error_intelligence_service import log_error

                for e in detected[:8]:
                    await log_error(
                        db, student_id=sess.student_id, language_id=sess.language_id,
                        error_type="grammar",
                        incorrect_form=(e.rule_explanation or e.original_text),
                        corrected_form=e.corrected_text,
                        context_sentence=e.original_text,
                    )
            except Exception:
                logger.warning(
                    "Exam error-intelligence logging failed session_id=%s user_id=%s",
                    session_id,
                    sess.student_id,
                )

            state["evaluation"] = {
                **dict(state.get("evaluation") or {}),
                "evaluation_status": "completed",
                "evaluation_completed_at": now.isoformat(),
                "evaluation_lease_expires_at": None,
            }
            _bump_state_revision(state)
            sess.exam_state = state
            flag_modified(sess, "exam_state")
            await db.commit()
            _cleanup_exam_audio(state)  # generated listening clips are no longer needed
            # Additive: seed the unified Learner Model from this placement (best-effort, never blocks).
            try:
                from app.services.language_learner_model_service import LanguageLearnerModelService

                # Seed ONLY skills the exam actually measured ΓÇö a skipped/empty section defaults to A2
                # above, and seeding that would fabricate "skill strength" for a skill never tested.
                seed_levels: dict[str, str] = {}
                if r_asked:
                    seed_levels["reading"] = reading_level.value
                if l_asked:
                    seed_levels["listening"] = listening_level.value
                if (wr.get("response") or "").strip():
                    seed_levels["writing"] = writing_level.value
                if sp_results:
                    seed_levels["speaking"] = speaking_level.value
                if seed_levels:
                    await LanguageLearnerModelService(db).seed_from_placement(
                        student_id=sess.student_id,
                        language_id=sess.language_id,
                        skill_levels=seed_levels,
                    )
            except Exception:  # pragma: no cover - never let seeding break the exam
                logger.warning(
                    "Learner-model placement seeding failed session_id=%s user_id=%s",
                    session_id,
                    sess.student_id,
                )
        except Exception as exc:  # pragma: no cover - safety net
            logger.error(
                "Exam evaluation failed session_id=%s error_type=%s",
                session_id,
                type(exc).__name__,
            )
            await db.rollback()
            sess = (
                await db.execute(
                    select(LanguageExamSession)
                    .where(LanguageExamSession.id == session_id)
                    .with_for_update()
                )
            ).scalar_one_or_none()
            if sess and sess.status != "completed":
                failed_state = dict(sess.exam_state or {})
                current_evaluation = dict(failed_state.get("evaluation") or {})
                if not secrets.compare_digest(
                    str(current_evaluation.get("evaluation_owner") or ""), evaluation_owner
                ):
                    return
                failed_state["evaluation"] = {
                    **current_evaluation,
                    "evaluation_status": "scorer_unavailable",
                    "evaluation_lease_expires_at": None,
                    "error_code": "scorer_unavailable",
                    "error_message": "The authoritative scorer is temporarily unavailable. Retry evaluation.",
                    "evaluation_failed_at": datetime.now(timezone.utc).isoformat(),
                }
                _bump_state_revision(failed_state)
                sess.exam_state = failed_state
                flag_modified(sess, "exam_state")
                sess.status = "failed"
                await db.commit()


# ---------------------------------------------------------------------------------------
# endpoints
# ---------------------------------------------------------------------------------------

async def _load_session(
    db: AsyncSession,
    session_id: str,
    student: User | int,
    *,
    for_update: bool = False,
) -> LanguageExamSession:
    student_id = int(student if isinstance(student, int) else student.id)
    stmt = select(LanguageExamSession).where(
        LanguageExamSession.id == session_id,
        LanguageExamSession.student_id == student_id,
    )
    if for_update:
        stmt = stmt.with_for_update().execution_options(populate_existing=True)
    sess = (await db.execute(stmt)).scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam session not found")
    return sess


def _cleanup_exam_audio(state: dict) -> None:
    """Delete the edge-tts listening clips generated for this attempt (best-effort)."""
    base = Path(get_settings().UPLOAD_DIR)
    for item in (state.get("listening", {}).get("pool") or {}).values():
        url = item.get("audio_url") or ""
        if not (url.startswith("/uploads/language_exam_audio/") or url.startswith("/uploads/exam_audio/")):
            continue
        try:
            (base / url[len("/uploads/") :]).unlink(missing_ok=True)
        except OSError:  # pragma: no cover
            pass


_PREP_RETRY_AFTER_S = 20


def _maybe_retrigger_prep(sess: LanguageExamSession, language_id: int, background_tasks: BackgroundTasks) -> bool:
    """Self-heal: if the current section's content never got generated (background task died /
    server restarted), re-launch _prepare_content ΓÇö but not more often than every 20s."""
    state = sess.exam_state or {}
    section = _current_section(state)
    if section not in PREPARED_SECTIONS:
        return False
    if state.get(section, {}).get("ready", True):
        return False
    last = state.get("content_prep_at")
    now = datetime.now(timezone.utc)
    if last:
        try:
            if (now - datetime.fromisoformat(last)).total_seconds() < _PREP_RETRY_AFTER_S:
                return False
        except (ValueError, TypeError):
            pass
    state["content_prep_at"] = now.isoformat()
    state["content_prep_token"] = _new_exam_token()
    state["content_prep_status"] = "preparing"
    sess.exam_state = state
    flag_modified(sess, "exam_state")
    background_tasks.add_task(_prepare_content, sess.id, language_id, state.get("start_level_hint") or "A2")
    return True


def _schedule_evaluation_recovery(
    sess: LanguageExamSession,
    background_tasks: BackgroundTasks,
) -> bool:
    if sess.status != "evaluating" or not _evaluation_should_run(sess.exam_state or {}):
        return False
    background_tasks.add_task(_run_evaluation, sess.id)
    return True


@router.post("/initiate", response_model=ExamStateOut)
async def initiate_exam(
    background_tasks: BackgroundTasks,
    student: User = Depends(require_active_language_subscription()),
    db: AsyncSession = Depends(get_db),
):
    """Resume an open 4-skill exam, or build a fresh one (speaking ready now; the reading/listening/
    writing content is generated fresh in the background while the student does the speaking part)."""
    language = await get_default_language(db)

    active_stmt = (
        select(LanguageExamSession)
        .where(
            LanguageExamSession.student_id == student.id,
            LanguageExamSession.language_id == language.id,
            LanguageExamSession.status.in_(("in_progress", "evaluating")),
            LanguageExamSession.exam_state.isnot(None),
        )
        .order_by(LanguageExamSession.created_at.desc())
        .limit(1)
    )

    # Phase 1: serialize the decision, then release the lock before scenario generation.
    await db.execute(select(User.id).where(User.id == student.id).with_for_update())
    profile = await ensure_language_profile(db, student.id, language.id)
    existing = (await db.execute(active_stmt.with_for_update())).scalar_one_or_none()
    if existing:
        check_or_raise("placement_poll", f"{student.id}:{existing.id}")
        state = copy.deepcopy(existing.exam_state or {})
        protocol_changed = _ensure_state_protocol(state)
        if protocol_changed:
            existing.exam_state = state
            flag_modified(existing, "exam_state")
        if existing.status == "in_progress":
            protocol_changed = _maybe_retrigger_prep(existing, language.id, background_tasks) or protocol_changed
        else:
            _schedule_evaluation_recovery(existing, background_tasks)
        if protocol_changed:
            state = copy.deepcopy(existing.exam_state or state)
            _bump_state_revision(state)
            existing.exam_state = state
            flag_modified(existing, "exam_state")
        await db.commit()
        return await _build_state_out(db, existing, resumed=True)

    ensure_placement_retake_allowed(profile)
    check_or_raise("placement_start", student.id)
    # Captured before commit: expire_on_commit would otherwise force a lazy reload of these
    # attributes on next access, which crashes (MissingGreenlet) once a slow external await
    # (the AI scenario call below) separates the commit from that access.
    student_id = int(student.id)
    language_id = int(language.id)
    await db.commit()

    # No row lock or database transaction remains open while the external examiner is called.
    level = await _effective_level(db, student_id=student_id, language_id=language_id)
    learner_grade = await _student_grade(db, student_id=student_id)
    await db.rollback()
    # MVP: prefer a curated, MVP-approved speaking_prompt bank item over live scenario/question
    # generation; fall back to the existing AI-generated (or grade-banded) path unchanged if the
    # bank has nothing usable for this level/language.
    opening_bank_item = await _speaking_bank_prompt(db, language_id=language_id, level_str=level)
    if opening_bank_item is not None:
        scenario = _speaking_scenario_from_bank_item(opening_bank_item)
    else:
        scenario = await ai_engine.generate_scenario_and_opening(effective_level=level, learner_grade=learner_grade)

    # Phase 2: recheck under the same per-user lock. A concurrent initiate may have won while AI
    # was running, in which case its session is returned and this generated scenario is discarded.
    await db.execute(select(User.id).where(User.id == student_id).with_for_update())
    existing = (await db.execute(active_stmt.with_for_update())).scalar_one_or_none()
    if existing:
        _schedule_evaluation_recovery(existing, background_tasks)
        await db.commit()
        return await _build_state_out(db, existing, resumed=True)
    profile = await ensure_language_profile(db, student_id, language_id)
    ensure_placement_retake_allowed(profile)

    state = {
        "version": 3,
        "state_revision": 1,
        "sections": list(SECTIONS),
        "cursor": 0,
        "start_level_hint": level,
        "learner_grade": learner_grade,
        "content_prep_at": datetime.now(timezone.utc).isoformat(),
        "content_prep_token": _new_exam_token(),
        "content_prep_status": "preparing",
        "speaking": {
            "scenario": {
                "scenario": scenario["scenario"],
                "ai_persona": scenario["ai_persona"],
                "student_role": scenario["student_role"],
                "setting": scenario["setting"],
            },
            "total_turns": SPEAKING_TURNS,
            "turn": 1,
            "pending_question": scenario["opening_question"],
            # Retained so the turn-1 answer can record which bank item it came from (or None for
            # AI-generated/fallback questions), mirroring bank_item_id retention in MCQ sections.
            "pending_bank_item_id": opening_bank_item.get("bank_item_id") if opening_bank_item is not None else None,
            # Retained so the next turn's selection can prefer an unseen subskill/task_type (soft
            # diversity preference) -- never read by scoring.
            "pending_bank_item_subskill": opening_bank_item.get("subskill") if opening_bank_item is not None else None,
            "turn_token": _new_exam_token(),
            "results": [],
            "done": False,
            "evidence_status": "missing_student_response",
        },
        # Filled in by the background _prepare_content task (until then: not ready).
        "listening": {"mode": "adaptive", "pool": {}, "current_level": "", "asked": [], "max_steps": ADAPTIVE_MAX_STEPS, "ready": False, "done": False, "evidence_status": "retry_required"},
        "reading": {"mode": "adaptive", "pool": {}, "current_level": "", "asked": [], "max_steps": ADAPTIVE_MAX_STEPS, "ready": False, "done": False, "evidence_status": "retry_required"},
        "grammar_vocab": {"mode": "adaptive", "pool": {}, "current_level": "", "asked": [], "max_steps": ADAPTIVE_MAX_STEPS, "ready": False, "done": False, "evidence_status": "retry_required"},
        "writing": {"prompt": "", "prompt_token": "", "min_words": WRITING_MIN_WORDS, "response": None, "ready": False, "done": False, "evidence_status": "retry_required"},
        # No "interview" section for new sessions (product decision: guided interview removed).
        # _ensure_interview_ready/_provisional_from_phase1/interview_opening stay in place as
        # dormant compatibility code for any already-persisted session whose own "sections" list
        # still includes "interview".
        "request_receipts": [],
    }
    sess = LanguageExamSession(
        student_id=student_id, language_id=language_id, current_step=1, max_steps=len(SECTIONS),
        exam_state=state, status="in_progress",
    )
    db.add(sess)
    await db.commit()
    background_tasks.add_task(_prepare_content, sess.id, language_id, level)
    return await _build_state_out(db, sess)


@router.get("/{session_id}/state", response_model=ExamStateOut)
async def get_state(
    session_id: str,
    background_tasks: BackgroundTasks,
    student: User = Depends(require_active_language_subscription()),
    db: AsyncSession = Depends(get_db),
):
    sess = await _load_session(db, session_id, student, for_update=True)
    check_or_raise("placement_poll", f"{student.id}:{session_id}")
    state = copy.deepcopy(sess.exam_state or {})
    changed = _ensure_state_protocol(state)
    if changed:
        sess.exam_state = state
        flag_modified(sess, "exam_state")
    if sess.status == "in_progress":
        changed = _maybe_retrigger_prep(sess, sess.language_id, background_tasks) or changed
    elif sess.status == "evaluating":
        _schedule_evaluation_recovery(sess, background_tasks)
    if changed:
        state = copy.deepcopy(sess.exam_state or state)
        _bump_state_revision(state)
        sess.exam_state = state
        flag_modified(sess, "exam_state")
    if changed or sess.status in {"in_progress", "evaluating"}:
        await db.commit()
    return await _build_state_out(db, sess)


@router.post("/{session_id}/abandon")
async def abandon_exam(
    session_id: str,
    student: User = Depends(require_active_language_subscription()),
    db: AsyncSession = Depends(get_db),
):
    """Abandon an unfinished attempt so the student can start a fresh one (escape a stuck state)."""
    sess = await _load_session(db, session_id, student, for_update=True)
    check_or_raise("placement_abandon", f"{student.id}:{session_id}")
    if sess.status == "evaluating":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "evaluation_in_progress", "message": "Evaluation is already in progress."},
        )
    if sess.status in ("in_progress", "failed"):
        abandoned_state = copy.deepcopy(sess.exam_state or {})
        _ensure_state_protocol(abandoned_state)
        abandoned_state["abandoned_at"] = datetime.now(timezone.utc).isoformat()
        _bump_state_revision(abandoned_state)
        sess.exam_state = abandoned_state
        flag_modified(sess, "exam_state")
        sess.status = "abandoned"
        await db.commit()
        _cleanup_exam_audio(abandoned_state)
    return {"ok": True, "status": sess.status}


def _maybe_finalize(sess: LanguageExamSession, state: dict, background_tasks: BackgroundTasks) -> bool:
    """If all sections are done, flip to evaluating and schedule the unified grading."""
    evaluation = dict(state.get("evaluation") or {})
    current_eval_status = str(evaluation.get("evaluation_status") or evaluation.get("status") or "")
    if sess.status == "in_progress" and _current_section(state) is None and current_eval_status not in {"pending", "running", "completed"}:
        _ensure_exam_evidence_complete(state)
        sess.status = "evaluating"
        state["evaluation"] = {
            **evaluation,
            "evaluation_status": "pending",
            "evaluation_started_at": None,
            "evaluation_lease_expires_at": None,
            "evaluation_attempt": int(evaluation.get("evaluation_attempt") or 0),
            "evaluation_owner": None,
        }
        background_tasks.add_task(_run_evaluation, sess.id)
        return True
    return False


async def _read_speaking_audio(file: UploadFile) -> ValidatedAudio:
    return await validate_placement_audio(file)


async def _verified_server_transcription(audio: ValidatedAudio):
    """Transcribe on the server and distinguish service failure from unusable speech."""
    stt = await transcribe_english_audio(
        audio.data,
        suffix=audio.suffix,
        audio_duration_s=audio.duration_seconds,
    )
    transcript = (stt.text or "").strip()
    error_code = str((stt.meta or {}).get("error_code") or "")
    if stt.engine in {"error", "disabled", "none"}:
        logger.warning(
            "Placement STT unavailable engine=%s",
            stt.engine,
        )
        client_error = error_code == "invalid_audio"
        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
                if client_error
                else status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail={
                "code": error_code or "stt_unavailable",
                "evidence_status": "retry_required",
                "message": (
                    "The recording could not be decoded. Please record it again."
                    if client_error
                    else "Speech transcription is temporarily unavailable. Please try again."
                ),
            },
        )
    rejection_code = str((stt.meta or {}).get("rejection_code") or "")
    if rejection_code:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": rejection_code,
                "evidence_status": "retry_required",
                "message": "The recording did not contain enough clear English speech. Please record again.",
            },
        )
    if (
        not transcript
        or len(transcript.split()) < 2
        or stt.low_confidence
        or (stt.no_speech_prob is not None and stt.no_speech_prob >= 0.55)
    ):
        logger.warning(
            "Placement speech rejected engine=%s low_confidence=%s",
            stt.engine,
            stt.low_confidence,
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "no_speech",
                "evidence_status": "retry_required",
                "message": "We could not hear a clear answer. Please check your microphone and record again.",
            },
        )
    return stt


@router.post("/{session_id}/speaking/turn", response_model=ExamStateOut)
async def speaking_turn(
    session_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    duration_seconds: float | None = Form(None, ge=0, le=180),
    request_id: str = Form(..., min_length=8, max_length=100),
    state_revision: int = Form(..., ge=1),
    turn_token: str = Form(..., min_length=16, max_length=200),
    student: User = Depends(require_active_language_subscription()),
    db: AsyncSession = Depends(get_db),
):
    """Transcribe once on the server, then merge the result under a short state lock."""
    sess = await _load_session(db, session_id, student)
    student_id = int(student.id)
    session_student_id = int(sess.student_id)
    language_id = int(sess.language_id)
    initial_status = str(sess.status)
    snapshot = copy.deepcopy(sess.exam_state or {})
    section = _current_section(snapshot)
    spoken_snapshot = snapshot.get(section, {})
    question = str(spoken_snapshot.get("pending_question") or "")
    expected_token = str(spoken_snapshot.get("turn_token") or "")
    turn = int(spoken_snapshot.get("turn") or 1)
    total = int(
        spoken_snapshot.get("total_turns")
        or (INTERVIEW_TURNS if section == "interview" else SPEAKING_TURNS)
    )
    scenario = copy.deepcopy(snapshot.get("speaking", {}).get("scenario", {}))
    guess = await _effective_level(
        db,
        student_id=session_student_id,
        language_id=language_id,
    )
    await db.rollback()

    _ = duration_seconds  # Server-decoded duration is authoritative.
    check_or_raise("placement_audio_turn", f"{student_id}:{session_id}")
    audio = await _read_speaking_audio(file)
    payload_hash = canonical_payload_hash(
        kind="speaking_turn",
        payload={
            "session_id": session_id,
            "state_revision": state_revision,
            "turn_token": turn_token,
            "audio_sha256": audio.sha256,
        },
    )
    existing_receipt = _request_receipt(
        snapshot,
        kind="speaking_turn",
        request_id=request_id,
        payload_hash=payload_hash,
    )
    if existing_receipt:
        current = await _load_session(db, session_id, student_id)
        return await _build_state_out(db, current)
    _require_state_revision(snapshot, supplied_revision=state_revision)
    if initial_status != "in_progress" or section not in SPEAKING_LIKE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "stale_exam_state", "current_state_revision": _state_revision(snapshot)},
        )
    _require_current_state(
        snapshot,
        supplied_revision=state_revision,
        supplied_token=turn_token,
        expected_token=expected_token,
    )
    if _audio_hash_already_used(snapshot, audio.sha256):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "duplicate_audio_evidence",
                "message": "Record a new answer for each speaking question.",
            },
        )
    stt = await _verified_server_transcription(audio)
    transcript = (stt.text or "").strip()
    assessment = await ai_engine.assess_speaking(
        transcript=transcript, scenario=scenario, question=question,
        turn=turn, total_turns=total, effective_level=guess, priming=spoken_snapshot.get("priming", ""),
        learner_grade=snapshot.get("learner_grade"),
    )

    # Re-read and validate after STT/AI. No row lock was held during either external call.
    sess = await _load_session(db, session_id, student_id, for_update=True)
    state = copy.deepcopy(sess.exam_state or {})
    existing_receipt = _request_receipt(
        state,
        kind="speaking_turn",
        request_id=request_id,
        payload_hash=payload_hash,
    )
    if existing_receipt:
        await db.commit()
        return await _build_state_out(db, sess)
    current_section = _current_section(state)
    current_spoken = state.get(current_section or "", {})
    _require_current_state(
        state,
        supplied_revision=state_revision,
        supplied_token=turn_token,
        expected_token=str(current_spoken.get("turn_token") or ""),
    )
    if sess.status != "in_progress" or current_section != section:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "stale_exam_state", "current_state_revision": _state_revision(state)},
        )
    if _audio_hash_already_used(state, audio.sha256):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "duplicate_audio_evidence", "message": "Record a new answer for each question."},
        )

    sp = state[section]
    answered_bank_item_id = sp.get("pending_bank_item_id")
    answered_bank_item_subskill = sp.get("pending_bank_item_subskill")
    sp.setdefault("results", []).append(
        {
            "question": question,
            "transcription": transcript,
            "grammar_vocab_feedback": assessment.grammar_vocab_feedback,
            "pronunciation_feedback": "",
            "pronunciation_status": "unassessed",
            "fluency_note": assessment.fluency_note,
            "estimated_level": assessment.estimated_level.value,
            "audio_sha256": audio.sha256,
            "audio_duration_seconds": audio.duration_seconds,
            "audio_mime_type": audio.mime_type,
            "stt_engine": stt.engine,
            "stt_model": stt.model,
            # Retained so the next turn's bank selection can exclude it via used_item_ids,
            # mirroring MCQ sections' bank_item_id retention (P1.1) -- scoring never reads this.
            "bank_item_id": int(answered_bank_item_id) if answered_bank_item_id else None,
            # Retained so the next turn's selection can prefer an unseen subskill/task_type (soft
            # diversity preference) -- never read by scoring.
            "bank_item_subskill": str(answered_bank_item_subskill) if answered_bank_item_subskill else None,
        }
    )

    feedback = SpeakingTurnFeedbackOut(
        transcription=transcript,
        grammar_vocab_feedback=assessment.grammar_vocab_feedback,
        pronunciation_feedback="Unassessed: no acoustic pronunciation scorer was used.",
        fluency_note=assessment.fluency_note,
    )

    if turn >= total:
        sp["done"] = True
        sp["pending_question"] = ""
        sp["pending_bank_item_id"] = None
        sp["pending_bank_item_subskill"] = None
        sp["turn_token"] = ""
        sp["evidence_status"] = "completed"
    else:
        sp["turn"] = turn + 1
        # MVP: prefer a curated bank prompt at the live estimated level (a light staircase) over
        # asking Claude to invent the next question; fall back to the existing AI-generated
        # question unchanged if the bank has nothing usable left. Interview (legacy, dormant)
        # keeps its own unmodified behavior -- this only applies to the live "speaking" section.
        next_bank_item = None
        if section == "speaking":
            next_bank_item = await _speaking_bank_prompt(
                db,
                language_id=language_id,
                level_str=assessment.estimated_level.value,
                used_item_ids=_already_used_speaking_bank_item_ids(state, section),
                used_subskills=_already_used_speaking_subskills(state, section),
            )
        if next_bank_item is not None:
            sp["pending_question"] = _speaking_bank_question_text(next_bank_item)
            sp["pending_bank_item_id"] = next_bank_item.get("bank_item_id")
            sp["pending_bank_item_subskill"] = next_bank_item.get("subskill")
        else:
            sp["pending_question"] = assessment.next_question or "Tell me more about that."
            sp["pending_bank_item_id"] = None
            sp["pending_bank_item_subskill"] = None
        sp["turn_token"] = _new_exam_token()
        sp["evidence_status"] = "missing_student_response"

    _advance_if_section_done(state)
    _maybe_finalize(sess, state, background_tasks)
    result_revision = _bump_state_revision(state)
    _record_request(
        state,
        kind="speaking_turn",
        request_id=request_id,
        payload_hash=payload_hash,
        request_revision=state_revision,
        token=turn_token,
        result_reference=f"{section}:{turn}:revision:{result_revision}",
    )
    sess.exam_state = state
    flag_modified(sess, "exam_state")
    await db.commit()
    return await _build_state_out(db, sess, last_feedback=feedback)


@router.post("/{session_id}/answer", response_model=ExamStateOut)
async def answer_mcq(
    session_id: str,
    body: McqAnswerIn,
    student: User = Depends(require_active_language_subscription()),
    db: AsyncSession = Depends(get_db),
):
    """Record an MCQ answer and advance to the next item/section."""
    sess = await _load_session(db, session_id, student, for_update=True)
    state = copy.deepcopy(sess.exam_state or {})
    payload_hash = canonical_payload_hash(
        kind="mcq_answer",
        payload={
            "session_id": session_id,
            "state_revision": body.state_revision,
            "question_token": body.question_token,
            "choice_index": body.choice_index,
        },
    )
    if _request_receipt(
        state,
        kind="mcq_answer",
        request_id=body.request_id,
        payload_hash=payload_hash,
    ):
        await db.commit()
        return await _build_state_out(db, sess)
    _require_state_revision(state, supplied_revision=body.state_revision)
    section = _current_section(state)
    if sess.status != "in_progress" or section not in MCQ_SECTIONS:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Not in an MCQ section")
    check_or_raise("placement_answer", f"{student.id}:{session_id}")

    sec = state[section]
    cur = sec.get("current_level")
    item = sec.get("pool", {}).get(cur)
    if sec.get("done") or not item:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No item awaiting an answer")
    _require_current_state(
        state,
        supplied_revision=body.state_revision,
        supplied_token=body.question_token,
        expected_token=str(item.get("question_token") or ""),
    )
    if body.choice_index >= len(item.get("options", [])):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="choice_index out of range")

    correct = body.choice_index == item.get("correct_index")
    bank_item_id = item.get("bank_item_id")
    if bank_item_id:
        await record_bank_item_answer(db, item_id=int(bank_item_id), correct=correct)
    sec.setdefault("asked", []).append({
        "level": cur,
        "correct": correct,
        "chosen_index": body.choice_index,
        # Retained so a later _prepare_content run can exclude it via used_item_ids (P1.1) —
        # scoring/adaptive logic never reads this key.
        "bank_item_id": int(bank_item_id) if bank_item_id else None,
    })
    asked_levels = {a["level"] for a in sec["asked"]}

    if sec.pop("_awaiting_boundary_answer", False):
        # P1.3: the one allotted boundary-confirmation question has now been answered — the
        # section always finishes here (regardless of correctness), so it can never ask a second.
        sec["done"] = True
        sec["evidence_status"] = "completed"
    else:
        # Adaptive staircase: harder if correct, easier if wrong; stop when converged / out of steps.
        nxt = adaptive_next_level(
            current=cur, correct=correct, asked_levels=asked_levels,
            pool_levels=set(sec.get("pool", {}).keys()),
            asked_count=len(sec["asked"]), max_steps=sec.get("max_steps", ADAPTIVE_MAX_STEPS),
        )
        if nxt is None:
            continuation = _mcq_continuation_level(
                pool_levels=set(sec.get("pool", {}).keys()),
                asked_levels=asked_levels,
                asked_count=len(sec["asked"]),
                current=cur,
            )
            boundary_item = None
            if continuation is None and not sec.get("boundary_asked"):
                boundary = _boundary_situation(sec["asked"])
                if boundary is not None:
                    sec["boundary_asked"] = True
                    low, high = boundary
                    boundary_item = await _boundary_confirmation_item(
                        db,
                        language_id=int(sess.language_id),
                        skill=section,
                        low=low,
                        high=high,
                        used_item_ids=_already_used_bank_item_ids(state, section),
                    )
            if continuation is not None:
                sec["current_level"] = continuation
                sec["evidence_status"] = "missing_student_response"
            elif boundary_item is not None:
                # P1.3: inject the boundary item under its own reported level so the existing
                # pool/current_level/asked machinery (and adaptive_result's CEFR parsing) needs no
                # changes; _awaiting_boundary_answer ensures this section finishes right after.
                boundary_item["question_token"] = _new_exam_token()
                level_key = boundary_item.get("level") or cur
                sec.setdefault("pool", {})[level_key] = boundary_item
                sec["current_level"] = level_key
                sec["_awaiting_boundary_answer"] = True
                sec["evidence_status"] = "missing_student_response"
            else:
                sec["done"] = True
                sec["evidence_status"] = "completed"
        else:
            sec["current_level"] = nxt
            sec["evidence_status"] = "missing_student_response"

    _advance_if_section_done(state)
    result_revision = _bump_state_revision(state)
    _record_request(
        state,
        kind="mcq_answer",
        request_id=body.request_id,
        payload_hash=payload_hash,
        request_revision=body.state_revision,
        token=body.question_token,
        result_reference=f"{section}:{cur}:revision:{result_revision}",
    )
    sess.exam_state = state
    flag_modified(sess, "exam_state")
    await db.commit()
    return await _build_state_out(db, sess)


@router.post("/{session_id}/writing")
async def submit_writing(
    session_id: str,
    body: WritingAnswerIn,
    background_tasks: BackgroundTasks,
    student: User = Depends(require_active_language_subscription()),
    db: AsyncSession = Depends(get_db),
):
    """Record the writing answer and flow into the Phase-2 spoken interview (or finalize)."""
    sess = await _load_session(db, session_id, student)
    snapshot = copy.deepcopy(sess.exam_state or {})
    payload_hash = canonical_payload_hash(
        kind="writing_answer",
        payload={
            "session_id": session_id,
            "state_revision": body.state_revision,
            "prompt_token": body.prompt_token,
            "text_sha256": hashlib.sha256(
                _normalise_writing_text(body.text).encode("utf-8")
            ).hexdigest(),
        },
    )
    if _request_receipt(
        snapshot,
        kind="writing_answer",
        request_id=body.request_id,
        payload_hash=payload_hash,
    ):
        return await _build_state_out(db, sess)
    _require_state_revision(snapshot, supplied_revision=body.state_revision)
    if sess.status != "in_progress" or _current_section(snapshot) != "writing":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Not in the writing section")
    _require_current_state(
        snapshot,
        supplied_revision=body.state_revision,
        supplied_token=body.prompt_token,
        expected_token=str(snapshot.get("writing", {}).get("prompt_token") or ""),
    )
    check_or_raise("placement_answer", f"{student.id}:{session_id}")

    min_words = snapshot.get("writing", {}).get("min_words", WRITING_MIN_WORDS)
    if len(body.text.split()) < min_words:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Your answer must be at least {min_words} words.",
        )

    # Build the interview opening from a prospective snapshot outside any lock/transaction.
    prospective = copy.deepcopy(snapshot)
    prospective["writing"]["response"] = body.text
    prospective["writing"]["done"] = True
    prospective["writing"]["evidence_status"] = "completed"
    _advance_if_section_done(prospective)
    await db.rollback()
    try:
        await _ensure_interview_ready(prospective)
    except Exception as exc:
        logger.warning(
            "Placement interview preparation failed session_id=%s error_type=%s",
            session_id,
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "content_unavailable",
                "message": "The interview prompt is temporarily unavailable. Please retry.",
            },
        ) from None

    # Merge under a fresh short lock and reject any state that moved while AI was running.
    sess = await _load_session(db, session_id, student, for_update=True)
    state = copy.deepcopy(sess.exam_state or {})
    if _request_receipt(
        state,
        kind="writing_answer",
        request_id=body.request_id,
        payload_hash=payload_hash,
    ):
        await db.commit()
        return await _build_state_out(db, sess)
    if sess.status != "in_progress" or _current_section(state) != "writing":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "stale_exam_state", "current_state_revision": _state_revision(state)},
        )
    _require_current_state(
        state,
        supplied_revision=body.state_revision,
        supplied_token=body.prompt_token,
        expected_token=str(state.get("writing", {}).get("prompt_token") or ""),
    )
    state["writing"]["response"] = body.text
    state["writing"]["done"] = True
    state["writing"]["evidence_status"] = "completed"
    _advance_if_section_done(state)
    if _current_section(state) == "interview":
        state["interview"] = copy.deepcopy(prospective["interview"])

    finalizing = _maybe_finalize(sess, state, background_tasks)
    result_revision = _bump_state_revision(state)
    _record_request(
        state,
        kind="writing_answer",
        request_id=body.request_id,
        payload_hash=payload_hash,
        request_revision=body.state_revision,
        token=body.prompt_token,
        result_reference=f"writing:revision:{result_revision}",
    )
    sess.exam_state = state
    flag_modified(sess, "exam_state")
    await db.commit()
    if finalizing:
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content=ExamProcessingOut(
                session_id=sess.id,
                message="Analyzing every skill and generating your placement report...",
            ).model_dump(),
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content=(await _build_state_out(db, sess)).model_dump())


@router.post(
    "/{session_id}/evaluation/retry",
    response_model=ExamProcessingOut,
    status_code=status.HTTP_202_ACCEPTED,
)
async def retry_exam_evaluation(
    session_id: str,
    background_tasks: BackgroundTasks,
    student: User = Depends(require_active_language_subscription()),
    db: AsyncSession = Depends(get_db),
):
    """Retry a failed authoritative evaluation without recollecting or duplicating evidence."""
    sess = await _load_session(db, session_id, student, for_update=True)
    check_or_raise("placement_evaluation_request", f"{student.id}:{session_id}")
    state = copy.deepcopy(sess.exam_state or {})
    if sess.status == "evaluating":
        evaluation = dict(state.get("evaluation") or {})
        evaluation_status = str(
            evaluation.get("evaluation_status") or evaluation.get("status") or "pending"
        )
        # A committed pending lease already represents a queued evaluation.  Treat a concurrent
        # retry as the same operation instead of bumping the revision and scheduling a duplicate.
        if evaluation_status == "pending" or (
            evaluation_status == "running" and not evaluation_lease_expired(state)
        ):
            await db.commit()
            return ExamProcessingOut(
                session_id=sess.id,
                message="Placement evaluation is already in progress.",
            )
        if evaluation_status != "running":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "evaluation_retry_not_allowed",
                    "message": "This evaluation cannot be retried from its current state.",
                },
            )
        # The former worker lost its lease. Clear ownership so exactly one new worker can claim it.
        evaluation.update(
            {
                "evaluation_status": "pending",
                "evaluation_owner": None,
                "evaluation_lease_expires_at": None,
                "retry_requested_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        state["evaluation"] = evaluation
        _bump_state_revision(state)
        sess.exam_state = state
        flag_modified(sess, "exam_state")
        await db.commit()
        background_tasks.add_task(_run_evaluation, sess.id)
        return ExamProcessingOut(
            session_id=sess.id,
            message="A stale placement evaluation has been queued again.",
        )
    if sess.status != "failed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "evaluation_retry_not_allowed", "message": "This evaluation cannot be retried."},
        )
    _ensure_exam_evidence_complete(state)
    state["evaluation"] = {
        **dict(state.get("evaluation") or {}),
        "evaluation_status": "pending",
        "evaluation_owner": None,
        "evaluation_lease_expires_at": None,
        "retry_requested_at": datetime.now(timezone.utc).isoformat(),
    }
    _bump_state_revision(state)
    sess.exam_state = state
    flag_modified(sess, "exam_state")
    sess.status = "evaluating"
    await db.commit()
    background_tasks.add_task(_run_evaluation, sess.id)
    return ExamProcessingOut(
        session_id=sess.id,
        message="Placement evaluation has been queued again.",
    )


@router.get("/{session_id}/report", response_model=ExamReportOut)
async def get_exam_report(
    session_id: str,
    student: User = Depends(require_active_language_subscription()),
    db: AsyncSession = Depends(get_db),
):
    """Poll for the final per-skill report (frontend shows a loader until status == completed)."""
    sess = await _load_session(db, session_id, student)
    check_or_raise("placement_poll", f"{student.id}:{session_id}")
    report = None
    if sess.assessment_report:
        try:
            report = MultiSkillReportSchema.model_validate(sess.assessment_report)
        except Exception:
            report = None
    evaluation = (sess.exam_state or {}).get("evaluation") or {}
    error_code = str(evaluation.get("error_code") or "") or None
    return ExamReportOut(
        session_id=sess.id, status=sess.status, is_completed=sess.is_completed,
        report=report, completed_at=sess.completed_at,
        error_code=error_code,
        error_message=("Placement evaluation failed. You can retry it." if error_code else None),
    )
