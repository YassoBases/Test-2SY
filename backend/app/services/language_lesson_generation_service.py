"""Nightly AI lesson generation — keep each (skill, level) lesson pool topped up.

A cron/off-peak job calls run_nightly_topup(); Claude generates fresh, CEFR-aligned lessons
(woven with the level's curriculum grammar/vocab themes), they are validated with the same
rules as the seed content, then stored as published LanguageContentItem rows. During the day
the normal lesson endpoints serve them from the (now larger, fresher) pool — no live AI cost.

Falls back to a no-op when Claude is unavailable, so the seeded 240 always remain.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.language.content import LanguageContentItem
from app.models.language.enums import LanguageLevel, LanguageSkill
from app.services.ai_service import generate_llm_json
from app.services.claude_service import is_claude_configured
from app.services.language_curriculum_service import get_level_curriculum
from app.services.language_subscription_service import get_default_language

logger = logging.getLogger(__name__)
settings = get_settings()

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
SKILLS = ["reading", "listening", "writing", "speaking"]
CONTENT_TYPE = {
    "reading": "lesson",
    "listening": "lesson",
    "writing": "writing_prompt",
    "speaking": "speaking_prompt",
}
# Keep at least this many published lessons available per (skill, level); generate the deficit.
TARGET_PER_BUCKET = 12
# Generate at most this many per call (keeps each LLM response small enough to not truncate).
MAX_PER_CALL = 3
# Rough reading passage length per CEFR level (listening uses ``language_cefr`` engine).
READING_WORDS_FOR_LEVEL = {"A1": 45, "A2": 70, "B1": 110, "B2": 170, "C1": 230, "C2": 280}
# Optional learner-chosen reading length, applied as a multiplier on the level's base word count.
LENGTH_MULTIPLIER = {"short": 0.6, "medium": 1.0, "long": 1.6}


def _parse(raw: str) -> list[dict] | None:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", (raw or "").strip())
    s, e = text.find("{"), text.rfind("}")
    if s == -1 or e == -1:
        return None
    try:
        data = json.loads(text[s : e + 1])
    except json.JSONDecodeError:
        return None
    items = data.get("items")
    return items if isinstance(items, list) and items else None


def _valid_mcq(body: dict) -> bool:
    qs = body.get("questions")
    if not isinstance(qs, list) or not qs:
        return False
    for q in qs:
        ch = q.get("choices")
        # 2-4 options: 4 for standard MCQ, 3 for True/False/Not Given, 2 for True/False.
        if not isinstance(ch, list) or not (2 <= len(ch) <= 4):
            return False
        ci = q.get("correct_index")
        if not isinstance(ci, int) or not (0 <= ci < len(ch)):
            return False
    return True


def _parse_weaknesses_from_context(adaptive_context: str) -> list[str]:
    for line in (adaptive_context or "").splitlines():
        if "weaknesses:" in line.lower():
            _, _, tail = line.partition(":")
            return [part.strip() for part in tail.split(",") if part.strip()]
    return []


def _build_prompt(skill: str, level: str, count: int, themes: str, topics: str = "", length: str = "", adaptive_context: str = "", *, quality_seed: str | None = None, listening_plan: object | None = None, curriculum_recommendation: object | None = None, goal_aware_recommendation: object | None = None, challenge_level: object | None = None, effective_difficulty_band: str | None = None) -> tuple[str, str]:
    from app.services.language_conversation_prompts import level_guidance

    theme_line = f" Reinforce these grammar/vocabulary themes where natural: {themes}." if themes else ""
    topic_line = f" Prefer topics the learner enjoys: {topics}." if topics else ""
    level_line = (
        f" Calibrate the difficulty precisely to CEFR {level} (apply the vocabulary, grammar and topic "
        f"complexity below; ignore any 'reply shape' note): {level_guidance(level)}"
    )
    common = (
        f"You are a CEFR curriculum author. Generate exactly {count} DISTINCT CEFR {level} "
        f"English {skill} lessons for Syrian learners (everyday/school-life topics)."
        f"{theme_line}{topic_line} ENGLISH ONLY — every field must be written in English (no Arabic)."
        + level_line
    )
    if skill == "reading":
        words = READING_WORDS_FOR_LEVEL.get(level, 100)
        if length in LENGTH_MULTIPLIER:
            words = max(25, round(words * LENGTH_MULTIPLIER[length]))
        # English-only, richer comprehension items: 5 mixed-type questions, each with a teaching
        # explanation and an exact supporting quote from the passage (for the UI to highlight).
        sys = (
            f"You are a CEFR curriculum author writing IELTS-style reading tasks. Generate exactly {count} "
            f"DISTINCT CEFR {level} English reading lessons for learners (everyday/integration topics)."
            f"{theme_line}{topic_line}{level_line} ENGLISH ONLY. "
            f"Each lesson: a ~{words}-word English passage + exactly 5 questions covering a MIX of these "
            "IELTS-style types:\n"
            "- main_idea / detail / inference / vocab_in_context: 4 choices, exactly one correct.\n"
            '- true_false_notgiven: a statement; choices MUST be EXACTLY ["True","False","Not Given"] '
            "(correct_index 0/1/2). Use 'Not Given' when the passage neither confirms nor contradicts it.\n"
            "- sentence_completion: a sentence summarising part of the passage with ONE blank shown as "
            "'_____'; 4 word/phrase options, exactly one correct.\n"
            "- heading_match: 'Which heading best fits the paragraph starting \"<first few words>\"?' with "
            "4 short heading options, exactly one correct.\n"
            "Include at least 2 of {true_false_notgiven, sentence_completion, heading_match} per lesson. "
            "For each question include a short English explanation, and evidence_quote = an EXACT substring "
            "copied from the passage that supports the answer (use \"\" for true_false_notgiven = Not Given). "
            "Also include glossary = 3-5 KEY words from the passage a learner at this level may not know, "
            "each with a short English definition (to pre-teach before reading). "
            'Return ONLY JSON: {"items":[{"title": str, "topic": str, "passage": str, '
            '"glossary":[{"word": str, "definition": str}], "questions":['
            '{"stem": str, "choices":[2-4 strings], "correct_index": int, '
            '"type": "main_idea|detail|inference|vocab_in_context|true_false_notgiven|sentence_completion|heading_match", '
            '"explanation": str, "evidence_quote": str}]}]}'
        )
    elif skill == "listening":
        from app.services.language_cefr.listening_runtime import (
            build_listening_cefr_profile_block,
            build_listening_generation_question_prompt_block,
        )
        from app.services.language_listening_quality import build_listening_quality_prompt_block

        cefr_block = build_listening_cefr_profile_block(level)
        question_block = build_listening_generation_question_prompt_block(level)
        if listening_plan is not None:
            band = effective_difficulty_band or listening_plan.difficulty_band.value
            quality_block = build_listening_quality_prompt_block(
                level,
                themes=themes,
                topics=topics,
                quality_spec=listening_plan.quality_spec,
                difficulty_band=band,
            )
        else:
            quality_block = build_listening_quality_prompt_block(
                level, themes=themes, topics=topics, seed=quality_seed
            )
        curriculum_block = ""
        if curriculum_recommendation is not None:
            from app.services.language_listening_curriculum import build_curriculum_prompt_block

            curriculum_block = f"\n\n{build_curriculum_prompt_block(curriculum_recommendation)}"
        goal_block = ""
        if goal_aware_recommendation is not None:
            from app.services.language_learning_goal import build_learning_goal_prompt_block

            goal_prompt = build_learning_goal_prompt_block(
                goal_aware_recommendation.learning_goal,
                plan=listening_plan,
                objective_hints=goal_aware_recommendation.goal_objective_hints,
            )
            goal_block = f"\n\n{goal_prompt}"
        challenge_block = ""
        if challenge_level is not None:
            from app.services.language_listening_challenge import build_adaptive_challenge_prompt_block

            challenge_block = f"\n\n{build_adaptive_challenge_prompt_block(level, challenge_level)}"
        sys = (
            f"You are a CEFR curriculum author writing Cambridge/IELTS-style listening tasks. "
            f"Generate exactly {count} DISTINCT CEFR {level} English listening lessons."
            f"{theme_line}{topic_line} ENGLISH ONLY.\n\n"
            f"{cefr_block}\n\n"
            f"{quality_block}{curriculum_block}{goal_block}{challenge_block}\n\n"
            "You MUST obey every constraint in [CEFR PROFILE]. "
            "You MUST follow every directive in [LISTENING QUALITY]. "
            "You MUST address [CURRICULUM FOCUS] when present. "
            "You MUST follow [LEARNING GOAL] style directives when present. "
            "You MUST follow [ADAPTIVE CHALLENGE] directives when present. "
            "The audio_transcript must match the transcript word-count and sentence-length bounds, "
            "use only allowed grammar, avoid forbidden grammar, match the vocabulary band, "
            "stay within suitable topics, and satisfy the listening objectives. "
            f"Each lesson: one natural spoken-English audio_transcript + {question_block}"
        )
    elif skill == "writing":
        sys = (
            common
            + " Each lesson: a clear writing prompt + a minimum word count appropriate to the level. "
            'Return ONLY JSON: {"items":[{"title": str, "prompt": str, '
            '"min_words": int, "min_sentences": int}]}'
        )
    else:  # speaking
        sys = (
            common
            + " Each lesson: a speaking prompt the learner answers aloud + a minimum duration in seconds. "
            'Return ONLY JSON: {"items":[{"title": str, "prompt": str, "min_seconds": int}]}'
        )
    # Phase 7 — prepend the learner's adaptive context (interests/weaknesses/effective level) BEFORE
    # the existing prompt, never replacing it (Prompt Enrichment Pattern). Empty = unchanged.
    if adaptive_context and adaptive_context.strip():
        sys = f"{adaptive_context.strip()}\n\n{sys}"
    user = f"Write the {count} CEFR {level} {skill} lessons now as JSON."
    return sys, user


def _to_body(skill: str, level: str, raw: dict, *, source: str = "ai_nightly") -> dict | None:
    """Normalize a raw generated item into a stored body_json; return None if invalid."""
    title = str(raw.get("title") or "").strip()
    if not title:
        return None
    # English-only: every stored field is English. The legacy *_ar keys are kept
    # for backward-compatible readers but now MIRROR the English text (never Arabic).
    title_ar = title
    body: dict = {"title_ar": title_ar, "source": source, "generated_at": datetime.now(timezone.utc).isoformat()}
    if skill == "reading":
        passage = str(raw.get("passage") or "").strip()
        if not passage:
            return None
        questions = []
        for i, q in enumerate(raw.get("questions") or [], start=1):
            if not isinstance(q, dict):
                continue
            questions.append({
                "id": q.get("id") or f"q{i}",
                "stem": str(q.get("stem") or "").strip(),
                "choices": q.get("choices") or [],
                "correct_index": q.get("correct_index"),
                "type": str(q.get("type") or "detail").strip(),
                "explanation": str(q.get("explanation") or "").strip(),
                "evidence_quote": str(q.get("evidence_quote") or "").strip(),
            })
        glossary = []
        for g in (raw.get("glossary") or [])[:6]:
            if isinstance(g, dict) and (g.get("word") or "").strip():
                glossary.append({
                    "word": str(g.get("word") or "").strip(),
                    "definition": str(g.get("definition") or "").strip(),
                })
        body.update(
            topic=str(raw.get("topic") or title).strip(),
            passage=passage,
            glossary=glossary,
            questions=questions,
        )
        if not _valid_mcq(body):
            return None
    elif skill == "listening":
        transcript = str(raw.get("audio_transcript") or "").strip()
        if not transcript:
            return None
        questions = []
        for i, q in enumerate(raw.get("questions") or [], start=1):
            if not isinstance(q, dict):
                continue
            questions.append({
                "id": q.get("id") or f"q{i}",
                "stem": str(q.get("stem") or "").strip(),
                "choices": q.get("choices") or [],
                "correct_index": q.get("correct_index"),
                "type": str(q.get("type") or "detail").strip(),
                "explanation": str(q.get("explanation") or "").strip(),
                "evidence_quote": str(q.get("evidence_quote") or "").strip(),
            })
        body.update(
            audio_transcript=transcript,
            instructions=str(raw.get("instructions") or "Listen and answer the questions.").strip(),
            questions=questions,
        )
        speakers_raw = raw.get("speakers")
        if isinstance(speakers_raw, list):
            speakers: list[dict] = []
            for idx, sp in enumerate(speakers_raw):
                if not isinstance(sp, dict):
                    continue
                name = str(sp.get("name") or "").strip()
                if not name:
                    continue
                speakers.append(
                    {
                        "id": str(sp.get("id") or f"speaker_{idx + 1}").strip(),
                        "name": name,
                        "gender": str(sp.get("gender") or "").strip().lower(),
                    }
                )
            if speakers:
                body["speakers"] = speakers
        if not _valid_mcq(body):
            return None
    elif skill == "writing":
        prompt = str(raw.get("prompt") or "").strip()
        if not prompt or not isinstance(raw.get("min_words"), int):
            return None
        body.update(
            prompt=prompt,
            prompt_ar=prompt,  # English-only: mirror the English prompt (legacy *_ar key)
            min_words=int(raw["min_words"]),
            min_sentences=int(raw.get("min_sentences") or 2),
        )
    else:  # speaking
        prompt = str(raw.get("prompt") or "").strip()
        if not prompt or not isinstance(raw.get("min_seconds"), int):
            return None
        body.update(
            prompt=prompt,
            prompt_ar=prompt,  # English-only: mirror the English prompt (legacy *_ar key)
            min_seconds=int(raw["min_seconds"]),
        )
    return {"title": title, "body": body}


def _log_listening_cefr_validation(
    *,
    level: str,
    attempt: int,
    report,
    title: str | None = None,
) -> None:
    from app.services.language_cefr.listening_validator import LISTENING_CEFR_MAX_ATTEMPTS

    status = "PASS" if report.passed else "FAIL"
    logger.info(
        "Listening CEFR validation level=%s attempt=%s/%s status=%s score=%s title=%s",
        level,
        attempt,
        LISTENING_CEFR_MAX_ATTEMPTS,
        status,
        report.score,
        title or "-",
    )
    if not report.passed:
        logger.warning(
            "Listening CEFR validation FAIL level=%s attempt=%s score=%s reasons=%s",
            level,
            attempt,
            report.score,
            report.failure_summary(),
        )


async def _generate_one_validated_listening(
    *,
    level: str,
    themes: str,
    topics: str,
    adaptive_context: str,
    store_source: str,
    existing: set[str],
    listening_plan: object | None = None,
    curriculum_recommendation: object | None = None,
    goal_aware_recommendation: object | None = None,
    challenge_level: object | None = None,
    effective_difficulty_band: str | None = None,
) -> tuple[dict | None, object | None]:
    """Generate one listening lesson and validate against the CEFR profile (up to 3 attempts)."""
    from app.services.language_cefr.listening_validator import (
        LISTENING_CEFR_MAX_ATTEMPTS,
        validate_listening_lesson,
    )

    last_report = None
    for attempt in range(1, LISTENING_CEFR_MAX_ATTEMPTS + 1):
        sys, user = _build_prompt(
            "listening",
            level,
            1,
            themes,
            topics,
            "",
            adaptive_context,
            listening_plan=listening_plan,
            curriculum_recommendation=curriculum_recommendation,
            goal_aware_recommendation=goal_aware_recommendation,
            challenge_level=challenge_level,
            effective_difficulty_band=effective_difficulty_band,
        )
        try:
            raw = await generate_llm_json(user, system=sys, temperature=0.7, max_output_tokens=8192)
        except Exception as exc:
            logger.warning("listening generation attempt %s failed [%s]: %s", attempt, level, exc)
            continue
        items = _parse(raw)
        if not items:
            logger.warning("listening generation attempt %s returned no JSON items [%s]", attempt, level)
            continue
        norm = _to_body("listening", level, items[0] if isinstance(items[0], dict) else {}, source=store_source)
        if not norm:
            logger.warning("listening generation attempt %s produced invalid body [%s]", attempt, level)
            continue
        if norm["title"] in existing:
            logger.info("listening generation attempt %s skipped duplicate title [%s]", attempt, norm["title"])
            continue
        last_report = validate_listening_lesson(norm["body"], level)
        _log_listening_cefr_validation(level=level, attempt=attempt, report=last_report, title=norm["title"])
        if last_report.passed:
            return norm, last_report
    return None, last_report


async def _generate_and_store_listening(
    db: AsyncSession,
    *,
    language_id: int,
    level: str,
    count: int,
    themes: str,
    topics: str,
    adaptive_context: str,
    student_id: int | None,
    store_source: str,
    body_extras: dict | None,
    existing: set[str],
    learning_goal: str | None = None,
) -> int:
    from app.services.language_cefr.listening_validator import ListeningCefrValidationExhaustedError
    from app.services.language_learning_goal import (
        GOAL_KEY,
        parse_learning_goal_from_context,
        resolve_learning_goal,
    )
    from app.services.language_listening_challenge import (
        LESSON_CHALLENGE_KEY,
        build_initial_challenge_state,
        load_student_challenge,
        recommend_challenge_adaptive_listening_plan,
        save_student_challenge,
    )
    from app.services.language_listening_confidence import (
        LESSON_CONFIDENCE_KEY,
        build_initial_confidence_state,
        load_student_confidence,
        save_student_confidence,
    )
    from app.services.language_listening_curriculum import (
        CURRICULUM_KEY,
        load_curriculum_history,
    )
    from app.services.language_listening_curriculum.types import CurriculumHistoryEntry
    from app.services.language_listening_intelligence import (
        HISTORY_KEY,
        load_listening_intelligence_history,
    )

    history = await load_listening_intelligence_history(
        db, language_id=language_id, level=level, student_id=student_id, limit=100
    )
    curriculum_history = await load_curriculum_history(
        db, language_id=language_id, level=level, student_id=student_id, limit=200
    )
    session_history = list(history)
    session_curriculum = list(curriculum_history)
    weaknesses = _parse_weaknesses_from_context(adaptive_context)
    resolved_goal = (
        resolve_learning_goal(explicit=learning_goal)
        if learning_goal
        else parse_learning_goal_from_context(adaptive_context)
    )
    if student_id is not None:
        confidence_state = await load_student_confidence(
            db, student_id=student_id, language_id=language_id, level=level
        )
        challenge_state = await load_student_challenge(
            db, student_id=student_id, language_id=language_id, level=level
        )
    else:
        confidence_state = build_initial_confidence_state(level)
        challenge_state = build_initial_challenge_state(level)

    inserted = 0
    for _ in range(count):
        challenge_recommendation = recommend_challenge_adaptive_listening_plan(
            level,
            session_history,
            session_curriculum,
            confidence_state,
            challenge_state,
            learning_goal=resolved_goal,
            themes=themes,
            topics=topics,
            weaknesses=weaknesses,
            generation_index=len(session_curriculum),
        )
        confidence_recommendation = challenge_recommendation.confidence_aware
        goal_recommendation = confidence_recommendation.goal_aware
        recommendation = confidence_recommendation.recommendation
        plan = recommendation.plan
        norm, report = await _generate_one_validated_listening(
            level=level,
            themes=themes,
            topics=topics,
            adaptive_context=adaptive_context,
            store_source=store_source,
            existing=existing,
            listening_plan=plan,
            curriculum_recommendation=recommendation,
            goal_aware_recommendation=goal_recommendation,
            challenge_level=challenge_recommendation.challenge_level,
            effective_difficulty_band=challenge_recommendation.effective_difficulty_band,
        )
        if norm is None:
            if count == 1:
                raise ListeningCefrValidationExhaustedError(level, report)  # type: ignore[arg-type]
            logger.error(
                "Listening CEFR validation exhausted without storing lesson level=%s",
                level,
            )
            break
        if body_extras:
            norm["body"].update(body_extras)
        norm["body"][HISTORY_KEY] = plan.to_metadata()
        norm["body"][CURRICULUM_KEY] = recommendation.to_metadata()
        if goal_recommendation is not None:
            norm["body"][GOAL_KEY] = goal_recommendation.to_metadata()
        norm["body"][LESSON_CONFIDENCE_KEY] = confidence_recommendation.to_metadata()
        norm["body"][LESSON_CHALLENGE_KEY] = challenge_recommendation.to_metadata()
        session_history.append(plan.to_history_entry())
        session_curriculum.append(
            CurriculumHistoryEntry(
                situation=plan.situation.value,
                category=plan.category.value,
                narrative_format=plan.narrative_format.value,
                skill_focus=recommendation.skill_focus,
                objectives=recommendation.objectives,
                knowledge_node=recommendation.knowledge_node,
                level=level,
                generation_index=len(session_curriculum),
                lesson_intent=recommendation.lesson_intent,
            )
        )
        existing.add(norm["title"])
        db.add(
            LanguageContentItem(
                language_id=language_id,
                student_id=student_id,
                skill=LanguageSkill.listening,
                level=LanguageLevel(level),
                content_type=CONTENT_TYPE["listening"],
                title=norm["title"],
                body_json=norm["body"],
                sort_order=0,
                is_published=True,
            )
        )
        inserted += 1
    if inserted and student_id is not None:
        await save_student_confidence(
            db, student_id=student_id, language_id=language_id, state=confidence_state
        )
        await save_student_challenge(
            db, student_id=student_id, language_id=language_id, state=challenge_state
        )
    if inserted:
        await db.flush()
    return inserted


async def _existing_titles(
    db: AsyncSession, *, language_id: int, skill: str, level: str, student_id: int | None = None
) -> set[str]:
    q = select(LanguageContentItem.title).where(
        LanguageContentItem.language_id == language_id,
        LanguageContentItem.skill == LanguageSkill(skill),
        LanguageContentItem.level == LanguageLevel(level),
        LanguageContentItem.content_type == CONTENT_TYPE[skill],
    )
    if student_id is not None:
        q = q.where(LanguageContentItem.student_id == student_id)
    else:
        q = q.where(LanguageContentItem.student_id.is_(None))
    rows = await db.execute(q)
    return {str(t).strip() for (t,) in rows.all() if t}


async def _published_count(db: AsyncSession, *, language_id: int, skill: str, level: str) -> int:
    res = await db.execute(
        select(func.count())
        .select_from(LanguageContentItem)
        .where(
            LanguageContentItem.language_id == language_id,
            LanguageContentItem.skill == LanguageSkill(skill),
            LanguageContentItem.level == LanguageLevel(level),
            LanguageContentItem.content_type == CONTENT_TYPE[skill],
            LanguageContentItem.is_published.is_(True),
            LanguageContentItem.student_id.is_(None),
        )
    )
    return int(res.scalar() or 0)


async def generate_and_store(
    db: AsyncSession,
    *,
    language_id: int,
    skill: str,
    level: str,
    count: int,
    topics: str = "",
    length: str = "",
    adaptive_context: str = "",
    student_id: int | None = None,
    source: str | None = None,
    body_extras: dict | None = None,
    learning_goal: str | None = None,
) -> int:
    """Generate up to `count` lessons for (skill, level) and store the valid, non-duplicate ones.

    ``topics`` (optional) nudges the generator toward subjects the learner enjoys (personalization).
    ``length`` (optional, reading) — short|medium|long passage length.
    ``adaptive_context`` (optional) — learner context block prepended to the prompt.
    ``student_id`` (optional) — when set, lessons are owned by that student only (personalized pool).
    ``source`` (optional) — body_json.source tag; defaults to ai_personalized when student_id is set.
    ``body_extras`` (optional) — extra keys merged into each stored body_json (e.g. profile hash).
    """
    if not is_claude_configured() or count <= 0:
        return 0
    store_source = source or ("ai_personalized" if student_id is not None else "ai_nightly")
    objectives = await get_level_curriculum(level)
    themes = ", ".join(
        f"{o.get('grammar') or ''} / {o.get('vocab') or ''}".strip(" /") for o in objectives[:5]
    )
    existing = await _existing_titles(
        db, language_id=language_id, skill=skill, level=level, student_id=student_id
    )
    if skill == "listening":
        return await _generate_and_store_listening(
            db,
            language_id=language_id,
            level=level,
            count=count,
            themes=themes,
            topics=topics,
            adaptive_context=adaptive_context,
            student_id=student_id,
            store_source=store_source,
            body_extras=body_extras,
            existing=existing,
            learning_goal=learning_goal,
        )
    inserted = 0
    remaining = count
    while remaining > 0:
        n = min(MAX_PER_CALL, remaining)
        sys, user = _build_prompt(skill, level, n, themes, topics, length, adaptive_context)
        try:
            raw = await generate_llm_json(user, system=sys, temperature=0.7, max_output_tokens=8192)
        except Exception as exc:
            logger.warning("lesson gen failed [%s][%s]: %s", skill, level, exc)
            break
        items = _parse(raw)
        if not items:
            break
        produced = 0
        for raw_item in items:
            norm = _to_body(
                skill, level, raw_item if isinstance(raw_item, dict) else {}, source=store_source
            )
            if not norm or norm["title"] in existing:
                continue
            if skill == "reading":
                # Tag the passage's length so the reader can be served the length it asked for.
                norm["body"]["reading_length"] = length if length in LENGTH_MULTIPLIER else "medium"
            if body_extras:
                norm["body"].update(body_extras)
            existing.add(norm["title"])
            db.add(
                LanguageContentItem(
                    language_id=language_id,
                    student_id=student_id,
                    skill=LanguageSkill(skill),
                    level=LanguageLevel(level),
                    content_type=CONTENT_TYPE[skill],
                    title=norm["title"],
                    body_json=norm["body"],
                    sort_order=0,
                    is_published=True,
                )
            )
            inserted += 1
            produced += 1
        await db.flush()
        remaining -= n
        if produced == 0:  # model returned nothing usable — stop hammering quota
            break
    return inserted


async def run_nightly_topup(
    db: AsyncSession, *, language_id: int | None = None, target: int = TARGET_PER_BUCKET
) -> dict:
    """Top every (skill, level) bucket up to `target` published lessons. Returns a summary."""
    if language_id is None:
        language = await get_default_language(db)
        language_id = language.id
    summary: dict[str, int] = {}
    total = 0
    for skill in SKILLS:
        for level in LEVELS:
            have = await _published_count(db, language_id=language_id, skill=skill, level=level)
            deficit = max(0, target - have)
            if deficit <= 0:
                continue
            made = await generate_and_store(db, language_id=language_id, skill=skill, level=level, count=deficit)
            if made:
                summary[f"{skill}_{level}"] = made
                total += made
    summary["_total"] = total
    return summary
