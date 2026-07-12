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

import logging
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
    SpeakingTranscriptionOut,
    SpeakingTurnFeedbackOut,
    WritingAnswerIn,
    WritingPromptOut,
)
from app.services.language_access_service import require_active_language_subscription
from app.services.language_exam_genai import ACCEPTED_AUDIO_MIME
from app.services.language_exam_service import (
    ALL_CEFR_LEVELS,
    adaptive_next_level,
    adaptive_result,
    ai_engine,
    cefr_from_rank,
    cefr_rank,
    overall_level,
)
from app.services.language_level_utils import primary_focus_and_strength
from app.services.language_placement_question_bank_service import (
    bank_item_to_exam_item,
    record_bank_item_answer,
    select_placement_bank_items,
)
from app.services.language_subscription_service import get_default_language
from app.services.language_transcription_service import transcribe_english_audio
from app.services.language_tts_service import synthesize_exam_audio

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/student/languages/exam", tags=["Language Exam"])

SECTIONS = ["speaking", "listening", "reading", "grammar_vocab", "writing", "interview"]
# Sections that work like the audio speaking flow (record -> assess -> next question).
SPEAKING_LIKE = {"speaking", "interview"}
MCQ_SECTIONS = {"listening", "reading", "grammar_vocab"}
PREPARED_SECTIONS = {"listening", "reading", "grammar_vocab", "writing"}
SPEAKING_TURNS = 3
INTERVIEW_TURNS = 2  # Phase 2 — guided follow-up seeded by Phase 1 evidence.
ADAPTIVE_MAX_STEPS = 5  # MCQ sections: max adaptive questions before settling on a level.
WRITING_MIN_WORDS = 40


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
    return {
        "mode": "adaptive",
        "pool": pool,
        "current_level": start_level if pool else "",
        "start_level": start_level,
        "asked": [],
        "max_steps": ADAPTIVE_MAX_STEPS,
        "ready": True,
        "done": not pool,
    }


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


async def _question_bank_pool(
    db: AsyncSession, *, language_id: int, skill: str, levels: list[str]
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


async def _prepare_content(session_id: str, language_id: int, level: str) -> None:
    """Background: generate fresh reading/listening/writing content (AI), voice listening clips
    with edge-tts, and write them into exam_state. Falls back to the seeded bank per skill if AI
    generation is unavailable, so the exam is never left without content.
    """
    async with AsyncSessionLocal() as db:
        sess = await db.get(LanguageExamSession, session_id)
        if not sess or not sess.exam_state:
            return
        # Adaptive comprehension covers the whole CEFR range; start near the student's estimate.
        start_level = level if level in ALL_CEFR_LEVELS else "B1"

        # NOTE: generation below is slow (LLM + several edge-tts calls) and runs WHILE the student
        # is doing the speaking section. We therefore build everything into locals first and only
        # merge the three sections into the LATEST state at the end ΓÇö never write back a stale
        # snapshot, which would clobber the speaking progress made meanwhile.

        # --- Reading: reviewed bank first, then AI/legacy fallbacks for missing levels. ---
        r_pool = await _question_bank_pool(
            db, language_id=language_id, skill="reading", levels=ALL_CEFR_LEVELS
        )
        missing = [lv for lv in ALL_CEFR_LEVELS if lv not in r_pool]
        try:
            gen = await ai_engine.generate_comprehension_set(skill="reading", levels=missing) if missing else None
        except Exception:  # pragma: no cover
            gen = None
        for it in (gen or {}).get("items", []):
            r_pool[it["level"]] = {
                "passage": it["text"], "situation": "", "question": it["question"],
                "options": it["options"], "correct_index": it["correct_index"], "level": it["level"],
            }
        missing = [lv for lv in ALL_CEFR_LEVELS if lv not in r_pool]
        if missing:
            for lv, item in (await _seeded_pool(db, language_id=language_id, skill=LanguageSkill.reading, levels=missing)).items():
                r_pool[lv] = item
        # Last resort: verified AI-generated question bank, so a level is never content-starved.
        missing = [lv for lv in ALL_CEFR_LEVELS if lv not in r_pool]
        if missing:
            for lv, item in (await _generated_pool(db, language_id=language_id, levels=missing)).items():
                r_pool[lv] = item
        reading_section = _new_adaptive_section(r_pool, start_level)

        # --- Grammar/vocabulary: reviewed bank only; it is diagnostic, not generated live. ---
        g_pool = await _question_bank_pool(
            db, language_id=language_id, skill="grammar_vocab", levels=ALL_CEFR_LEVELS
        )
        grammar_vocab_section = _new_adaptive_section(g_pool, start_level)

        # --- Listening: reviewed bank first, then AI/legacy fallbacks for missing levels. ---
        l_pool = await _question_bank_pool(
            db, language_id=language_id, skill="listening", levels=ALL_CEFR_LEVELS
        )
        missing = [lv for lv in ALL_CEFR_LEVELS if lv not in l_pool]
        try:
            gen = await ai_engine.generate_comprehension_set(skill="listening", levels=missing) if missing else None
        except Exception:  # pragma: no cover
            gen = None
        for it in (gen or {}).get("items", []):
            audio_url = await synthesize_exam_audio(it["text"])
            l_pool[it["level"]] = {
                "audio_url": audio_url, "audio_text": it["text"], "situation": it["situation"], "question": it["question"],
                "options": it["options"], "correct_index": it["correct_index"], "level": it["level"],
            }
        missing = [lv for lv in ALL_CEFR_LEVELS if lv not in l_pool]
        if missing:
            for lv, item in (await _seeded_pool(db, language_id=language_id, skill=LanguageSkill.listening, levels=missing)).items():
                l_pool[lv] = item
        listening_section = _new_adaptive_section(l_pool, start_level)
        current_listening = listening_section.get("pool", {}).get(listening_section.get("current_level"))
        if current_listening:
            await _materialize_listening_audio(db, current_listening)

        # --- Writing: reviewed bank first, AI next, legacy/generic final fallback. ---
        wp = await _writing_prompt(db, language_id=language_id, level_str=level, include_generic=False)
        if not wp:
            try:
                wp = await ai_engine.generate_writing_prompt(level=level)
            except Exception:  # pragma: no cover
                wp = None
        if not wp:
            wp = await _writing_prompt(db, language_id=language_id, level_str=level, include_generic=True)
        writing_section = {
            "prompt": wp, "min_words": WRITING_MIN_WORDS, "response": None, "ready": True, "done": False,
        }

        # --- Merge into the freshest state (re-read to avoid clobbering concurrent progress) ---
        await db.refresh(sess, ["exam_state"])
        state = dict(sess.exam_state or {})
        state["reading"] = reading_section
        state["listening"] = listening_section
        state["grammar_vocab"] = grammar_vocab_section
        state["writing"] = writing_section
        sess.exam_state = state
        flag_modified(sess, "exam_state")
        await db.commit()


async def _writing_prompt(
    db: AsyncSession, *, language_id: int, level_str: str, include_generic: bool = True
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
    """Render the current section into the frontend contract (lazily resolving listening audio)."""
    state = sess.exam_state or {}
    sections = state.get("sections", SECTIONS)
    cursor = state.get("cursor", 0)

    if sess.status in ("evaluating", "completed", "failed") or cursor >= len(sections):
        phase = "completed" if sess.status == "completed" else "evaluating"
        return ExamStateOut(
            session_id=sess.id, phase=phase, section_index=len(sections),
            section_total=len(sections), sections=sections, resumed=resumed,
        )

    section = sections[cursor]

    # Reading/listening/writing content is generated in the background; until it's ready, tell the
    # frontend to show a loader and poll. (Older sessions without the flag are treated as ready.)
    if section in PREPARED_SECTIONS and not state.get(section, {}).get("ready", True):
        return ExamStateOut(
            session_id=sess.id, phase="preparing", section_index=cursor,
            section_total=len(sections), sections=sections, resumed=resumed,
        )

    out = ExamStateOut(
        session_id=sess.id, phase=section, section_index=cursor, section_total=len(sections),
        sections=sections, last_feedback=last_feedback, resumed=resumed,
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
        )
    elif section in MCQ_SECTIONS:
        sec = state[section]
        item = sec.get("pool", {}).get(sec.get("current_level"))
        if item and not sec.get("done"):
            audio_url = None
            audio_text = None
            passage = item.get("passage") or None if section == "reading" else None
            situation = item.get("situation") or None if section == "listening" else None
            instructions = "Choose the best answer."
            if section == "listening":
                instructions = "Listen to the clip, then answer."
                audio_url, audio_text, audio_created = await _materialize_listening_audio(db, item)
                if audio_created:
                    sess.exam_state = state
                    flag_modified(sess, "exam_state")
                    await db.commit()
                audio_text = None if audio_url else audio_text
            elif section == "reading":
                instructions = "Read the passage, then answer."
            elif section == "grammar_vocab":
                instructions = "Choose the most accurate English option."
            out.mcq = McqPromptOut(
                instructions=instructions,
                passage=passage,
                audio_url=audio_url,
                audio_text=audio_text,
                situation=situation,
                question=item.get("question", ""),
                options=item.get("options", []),
                item_index=len(sec.get("asked", [])),
                item_total=sec.get("max_steps", ADAPTIVE_MAX_STEPS),
            )
    elif section == "writing":
        wr = state["writing"]
        out.writing = WritingPromptOut(prompt=wr.get("prompt", ""), min_words=wr.get("min_words", WRITING_MIN_WORDS))

    return out


async def _resolve_listening_audio(db: AsyncSession, item: dict) -> str | None:
    """Return only audio that is tied to the same transcript as the question.

    Placement listening is transcript-led: if we cannot prove the audio belongs to this item, the
    frontend will read `audio_text` with browser speech instead of playing a mismatched lesson clip.
    """

    audio_url = item.get("audio_url")
    if _is_usable_audio_url(audio_url):
        return str(audio_url)

    content_item_id = item.get("content_id")
    if not content_item_id:
        return None

    content = await db.get(LanguageContentItem, content_item_id)
    body = content.body_json if content else {}
    body_audio_url = (body or {}).get("audio_url")
    if _listening_text_from_body(body) and _is_usable_audio_url(body_audio_url):
        return str(body_audio_url)
    return None


async def _resolve_listening_audio_text(db: AsyncSession, item: dict) -> str | None:
    text = str(item.get("audio_text") or "").strip()
    if text:
        return text

    content_item_id = item.get("content_id")
    if not content_item_id:
        return None
    content = await db.get(LanguageContentItem, content_item_id)
    body = content.body_json if content else {}
    text = _listening_text_from_body(body)
    return text or None


async def _materialize_listening_audio(db: AsyncSession, item: dict) -> tuple[str | None, str | None, bool]:
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
        logger.warning("Placement listening TTS failed: %s", exc)

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


# ---------------------------------------------------------------------------------------
# background final evaluation
# ---------------------------------------------------------------------------------------

# Realistic study time to climb one CEFR band (higher bands take longer); C2 = already top.
_WEEKS_TO_NEXT = {"A1": 10, "A2": 12, "B1": 16, "B2": 20, "C1": 24, "C2": 0}


def _weeks_to_next_level(level: CEFRLevel) -> int:
    return _WEEKS_TO_NEXT.get(level.value, 14)


async def _run_evaluation(session_id: str) -> None:
    """Fuse all four sections into a per-skill report, persist it, and unlock the module."""
    async with AsyncSessionLocal() as db:
        sess = await db.get(LanguageExamSession, session_id)
        if not sess or sess.status != "evaluating":
            return
        try:
            state = sess.exam_state or {}
            now = datetime.now(timezone.utc)

            # --- Shared: per-turn evidence block + effective-level guess.
            def _block(results: list[dict]) -> str:
                return "\n".join(
                    f"- Q: {r.get('question','')}\n  Said: {r.get('transcription','')}\n  "
                    f"Notes: {r.get('grammar_vocab_feedback','')} | {r.get('pronunciation_feedback','')} | {r.get('fluency_note','')}"
                    for r in results
                ) or "(none)"

            guess = await _effective_level(db, student_id=sess.student_id, language_id=sess.language_id)

            # --- Speaking: independent 4-criteria rubric over Phase-1 + Phase-2 turns.
            ph1_results = state.get("speaking", {}).get("results", [])
            ph2_results = state.get("interview", {}).get("results", [])
            sp_results = ph1_results + ph2_results
            live_available = bool(ph2_results)
            sp_evidence = (
                f"PHASE 1 ΓÇö ROLE-PLAY SPEAKING:\n{_block(ph1_results)}\n\n"
                f"PHASE 2 ΓÇö GUIDED INTERVIEW:\n{_block(ph2_results)}"
            )
            sp_detected: list = []
            if sp_results:
                sp_grade = await ai_engine.grade_speaking(evidence=sp_evidence, effective_level=guess)
                speaking_level, speaking_score = sp_grade.level, sp_grade.score
                speaking_breakdown = {
                    "fluency": sp_grade.fluency, "lexical": sp_grade.lexical,
                    "grammar": sp_grade.grammar, "pronunciation": sp_grade.pronunciation,
                }
                sp_detected = list(sp_grade.detected_errors)
            else:
                speaking_level, speaking_score, speaking_breakdown = CEFRLevel.A2, 0.0, {}

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

            # --- Narrative from all evidence (weight spoken for fluency/pronunciation,
            #     written for grammar/vocab).
            grammar_evidence = (
                f"GRAMMAR/VOCAB: {g_correct}/{g_total} correct -> {grammar_vocab_level.value}\n\n"
                if g_asked
                else "GRAMMAR/VOCAB: not measured\n\n"
            )
            evidence = (
                "Weighting: spoken speech is the stronger signal for fluency & pronunciation; "
                "written items anchor grammar & vocabulary.\n\n"
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
                    "pronunciation_feedback": r.get("pronunciation_feedback", ""),
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
            )

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
            prof.next_allowed_retake_date = now + timedelta(days=90)
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
                logger.warning("exam error-intelligence logging failed", exc_info=True)

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
                logger.warning("Learner-model placement seeding failed (non-blocking)", exc_info=True)
        except Exception:  # pragma: no cover - safety net
            logger.exception("Exam evaluation failed for session %s", session_id)
            await db.rollback()
            sess = await db.get(LanguageExamSession, session_id)
            if sess:
                sess.status = "failed"
                await db.commit()


# ---------------------------------------------------------------------------------------
# endpoints
# ---------------------------------------------------------------------------------------

async def _load_session(db: AsyncSession, session_id: str, student: User) -> LanguageExamSession:
    sess = await db.get(LanguageExamSession, session_id)
    if not sess or sess.student_id != student.id:
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


def _maybe_retrigger_prep(sess: LanguageExamSession, language_id: int, background_tasks: BackgroundTasks) -> None:
    """Self-heal: if the current section's content never got generated (background task died /
    server restarted), re-launch _prepare_content ΓÇö but not more often than every 20s."""
    state = sess.exam_state or {}
    section = _current_section(state)
    if section not in PREPARED_SECTIONS:
        return
    if state.get(section, {}).get("ready", True):
        return
    last = state.get("content_prep_at")
    now = datetime.now(timezone.utc)
    if last:
        try:
            if (now - datetime.fromisoformat(last)).total_seconds() < _PREP_RETRY_AFTER_S:
                return
        except (ValueError, TypeError):
            pass
    state["content_prep_at"] = now.isoformat()
    sess.exam_state = state
    flag_modified(sess, "exam_state")
    background_tasks.add_task(_prepare_content, sess.id, language_id, state.get("start_level_hint") or "A2")


@router.post("/initiate", response_model=ExamStateOut)
async def initiate_exam(
    background_tasks: BackgroundTasks,
    student: User = Depends(require_active_language_subscription()),
    db: AsyncSession = Depends(get_db),
):
    """Resume an open 4-skill exam, or build a fresh one (speaking ready now; the reading/listening/
    writing content is generated fresh in the background while the student does the speaking part)."""
    language = await get_default_language(db)

    existing = (
        await db.execute(
            select(LanguageExamSession)
            .where(
                LanguageExamSession.student_id == student.id,
                LanguageExamSession.status == "in_progress",
                LanguageExamSession.exam_state.isnot(None),
            )
            .order_by(LanguageExamSession.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if existing:
        # Self-heal a stuck attempt whose background content generation never finished.
        _maybe_retrigger_prep(existing, language.id, background_tasks)
        await db.commit()
        return await _build_state_out(db, existing, resumed=True)

    level = await _effective_level(db, student_id=student.id, language_id=language.id)
    learner_grade = await _student_grade(db, student_id=student.id)
    scenario = await ai_engine.generate_scenario_and_opening(effective_level=level, learner_grade=learner_grade)

    state = {
        "version": 2,
        "sections": list(SECTIONS),
        "cursor": 0,
        "start_level_hint": level,
        "learner_grade": learner_grade,
        "content_prep_at": datetime.now(timezone.utc).isoformat(),
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
            "results": [],
            "done": False,
        },
        # Filled in by the background _prepare_content task (until then: not ready).
        "listening": {"mode": "adaptive", "pool": {}, "current_level": "", "asked": [], "max_steps": ADAPTIVE_MAX_STEPS, "ready": False, "done": False},
        "reading": {"mode": "adaptive", "pool": {}, "current_level": "", "asked": [], "max_steps": ADAPTIVE_MAX_STEPS, "ready": False, "done": False},
        "grammar_vocab": {"mode": "adaptive", "pool": {}, "current_level": "", "asked": [], "max_steps": ADAPTIVE_MAX_STEPS, "ready": False, "done": False},
        "writing": {"prompt": "", "min_words": WRITING_MIN_WORDS, "response": None, "ready": False, "done": False},
        "interview": {
            "priming": "",
            "total_turns": INTERVIEW_TURNS,
            "turn": 1,
            "pending_question": "",
            "results": [],
            "done": False,
        },
    }
    sess = LanguageExamSession(
        student_id=student.id, language_id=language.id, current_step=1, max_steps=len(SECTIONS),
        exam_state=state, status="in_progress",
    )
    db.add(sess)
    await db.commit()
    background_tasks.add_task(_prepare_content, sess.id, language.id, level)
    return await _build_state_out(db, sess)


@router.get("/{session_id}/state", response_model=ExamStateOut)
async def get_state(
    session_id: str,
    background_tasks: BackgroundTasks,
    student: User = Depends(require_active_language_subscription()),
    db: AsyncSession = Depends(get_db),
):
    sess = await _load_session(db, session_id, student)
    if sess.status == "in_progress":
        _maybe_retrigger_prep(sess, sess.language_id, background_tasks)
        await db.commit()
    return await _build_state_out(db, sess)


@router.post("/{session_id}/abandon")
async def abandon_exam(
    session_id: str,
    student: User = Depends(require_active_language_subscription()),
    db: AsyncSession = Depends(get_db),
):
    """Abandon an unfinished attempt so the student can start a fresh one (escape a stuck state)."""
    sess = await _load_session(db, session_id, student)
    if sess.status not in ("completed",):
        sess.status = "abandoned"
        _cleanup_exam_audio(sess.exam_state or {})
        await db.commit()
    return {"ok": True, "status": sess.status}


def _maybe_finalize(sess: LanguageExamSession, state: dict, background_tasks: BackgroundTasks) -> bool:
    """If all sections are done, flip to evaluating and schedule the unified grading."""
    if _current_section(state) is None:
        sess.status = "evaluating"
        background_tasks.add_task(_run_evaluation, sess.id)
        return True
    return False


async def _read_speaking_audio(file: UploadFile) -> tuple[bytes, str, str]:
    """Validate one browser/uploaded audio answer and return bytes, MIME and suffix."""
    mime = (file.content_type or "").split(";")[0].strip().lower()
    if mime not in ACCEPTED_AUDIO_MIME:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported audio type: {mime or 'unknown'}",
        )
    cap = settings_max_bytes()
    data = await file.read(cap + 1)
    if len(data) > cap:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Audio file too large")
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty audio file")
    return data, mime, ACCEPTED_AUDIO_MIME[mime]


async def _gpt4o_transcript(data: bytes, suffix: str) -> SpeakingTranscriptionOut:
    stt = await transcribe_english_audio(data, suffix=suffix)
    transcript = (stt.text or "").strip()
    if not transcript:
        logger.warning("Placement speaking STT returned no text: engine=%s meta=%s", stt.engine, stt.meta)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="We could not hear a clear answer. Please check your microphone and record again.",
        )
    return SpeakingTranscriptionOut(
        transcription=transcript,
        engine=stt.engine,
        model=stt.model,
    )


@router.post("/{session_id}/speaking/transcribe", response_model=SpeakingTranscriptionOut)
async def transcribe_speaking_answer(
    session_id: str,
    file: UploadFile = File(...),
    student: User = Depends(require_active_language_subscription()),
    db: AsyncSession = Depends(get_db),
):
    """Transcribe an answer for preview without advancing or scoring the exam."""
    sess = await _load_session(db, session_id, student)
    if sess.status != "in_progress" or _current_section(sess.exam_state or {}) not in SPEAKING_LIKE:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Not in a speaking section")
    data, _mime, suffix = await _read_speaking_audio(file)
    return await _gpt4o_transcript(data, suffix)


@router.post("/{session_id}/speaking/turn", response_model=ExamStateOut)
async def speaking_turn(
    session_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    duration_seconds: float | None = Form(None),
    transcription: str | None = Form(None),
    student: User = Depends(require_active_language_subscription()),
    db: AsyncSession = Depends(get_db),
):
    """Assess one spoken answer from the audio; advances the speaking OR interview section."""
    sess = await _load_session(db, session_id, student)
    state = sess.exam_state or {}
    section = _current_section(state)
    if sess.status != "in_progress" or section not in SPEAKING_LIKE:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Not in a speaking section")

    data, _mime, suffix = await _read_speaking_audio(file)
    transcript = (transcription or "").strip()
    if not transcript:
        transcript = (await _gpt4o_transcript(data, suffix)).transcription

    sp = state[section]
    turn = sp.get("turn", 1)
    total = sp.get("total_turns", INTERVIEW_TURNS if section == "interview" else SPEAKING_TURNS)
    question = sp.get("pending_question", "")
    scenario = state.get("speaking", {}).get("scenario", {})
    guess = await _effective_level(db, student_id=sess.student_id, language_id=sess.language_id)

    assessment = await ai_engine.assess_speaking(
        transcript=transcript, scenario=scenario, question=question,
        turn=turn, total_turns=total, effective_level=guess, priming=sp.get("priming", ""),
        learner_grade=state.get("learner_grade"),
    )
    sp.setdefault("results", []).append(
        {
            "question": question,
            "transcription": assessment.transcription,
            "grammar_vocab_feedback": assessment.grammar_vocab_feedback,
            "pronunciation_feedback": assessment.pronunciation_feedback,
            "fluency_note": assessment.fluency_note,
            "estimated_level": assessment.estimated_level.value,
        }
    )

    feedback = SpeakingTurnFeedbackOut(
        transcription=assessment.transcription,
        grammar_vocab_feedback=assessment.grammar_vocab_feedback,
        pronunciation_feedback=assessment.pronunciation_feedback,
        fluency_note=assessment.fluency_note,
    )

    if turn >= total:
        sp["done"] = True
        sp["pending_question"] = ""
    else:
        sp["turn"] = turn + 1
        sp["pending_question"] = assessment.next_question or "Tell me more about that."

    _advance_if_section_done(state)
    await _ensure_interview_ready(state)  # prep Phase 2 if we just entered it
    _maybe_finalize(sess, state, background_tasks)
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
    sess = await _load_session(db, session_id, student)
    state = sess.exam_state or {}
    section = _current_section(state)
    if sess.status != "in_progress" or section not in MCQ_SECTIONS:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Not in an MCQ section")

    sec = state[section]
    cur = sec.get("current_level")
    item = sec.get("pool", {}).get(cur)
    if sec.get("done") or not item:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No item awaiting an answer")
    if body.choice_index >= len(item.get("options", [])):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="choice_index out of range")

    correct = body.choice_index == item.get("correct_index")
    bank_item_id = item.get("bank_item_id")
    if bank_item_id:
        await record_bank_item_answer(db, item_id=int(bank_item_id), correct=correct)
    sec.setdefault("asked", []).append({"level": cur, "correct": correct, "chosen_index": body.choice_index})
    asked_levels = {a["level"] for a in sec["asked"]}

    # Adaptive staircase: harder if correct, easier if wrong; stop when converged / out of steps.
    nxt = adaptive_next_level(
        current=cur, correct=correct, asked_levels=asked_levels,
        pool_levels=set(sec.get("pool", {}).keys()),
        asked_count=len(sec["asked"]), max_steps=sec.get("max_steps", ADAPTIVE_MAX_STEPS),
    )
    if nxt is None:
        sec["done"] = True
    else:
        sec["current_level"] = nxt

    _advance_if_section_done(state)
    await _ensure_interview_ready(state)
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
    state = sess.exam_state or {}
    if sess.status != "in_progress" or _current_section(state) != "writing":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Not in the writing section")

    min_words = state.get("writing", {}).get("min_words", WRITING_MIN_WORDS)
    if len(body.text.split()) < min_words:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Your answer must be at least {min_words} words.",
        )

    state["writing"]["response"] = body.text
    state["writing"]["done"] = True
    _advance_if_section_done(state)
    await _ensure_interview_ready(state)  # build Phase-2 priming + opening question

    finalizing = _maybe_finalize(sess, state, background_tasks)
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


@router.get("/{session_id}/report", response_model=ExamReportOut)
async def get_exam_report(
    session_id: str,
    student: User = Depends(require_active_language_subscription()),
    db: AsyncSession = Depends(get_db),
):
    """Poll for the final per-skill report (frontend shows a loader until status == completed)."""
    sess = await _load_session(db, session_id, student)
    report = None
    if sess.assessment_report:
        try:
            report = MultiSkillReportSchema.model_validate(sess.assessment_report)
        except Exception:
            report = None
    return ExamReportOut(
        session_id=sess.id, status=sess.status, is_completed=sess.is_completed,
        report=report, completed_at=sess.completed_at,
    )


def settings_max_bytes() -> int:
    return max(1, get_settings().GENAI_EXAM_MAX_AUDIO_MB) * 1024 * 1024
