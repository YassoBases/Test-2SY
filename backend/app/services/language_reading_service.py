"""Adaptive, self-replenishing reading practice.

Serves one reading passage at a time at the student's current reading level (adaptive — the level
is nudged up/down by performance in submit_reading), generating fresh AI content on demand when the
bank runs low so the supply is effectively infinite.
"""

from __future__ import annotations

import json
import logging
import re

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.language.analytics import LanguageAnalytics
from app.models.language.content import LanguageContentItem
from app.models.language.engagement import LanguageActivityLog
from app.models.language.enums import LanguageContentProgressStatus, LanguageLevel, LanguageSkill
from app.models.language.profile import LanguageStudentProfile
from app.models.language.progress import LanguageReadingProgress
from app.services.ai_service import generate_llm_json
from app.services.language_cache import TTLCache
from app.services.language_conversation_prompts import level_calibration_line
from app.services.language_generation_gate import (
    can_generate,
    note_failure as note_generation_failure,
    note_success as note_generation_success,
)
from app.services.language_content_service import get_reading_lesson, lesson_body_for_student
from app.services.language_learner_events import component_for_question
from app.services.language_lesson_generation_service import generate_and_store
from app.services.language_level_utils import CEFR_RANK, RANK_CEFR
from app.services.language_subscription_service import get_default_language

logger = logging.getLogger(__name__)

_ON_DEMAND_BATCH = 3

# Curated reading interests the learner can opt into (drives generated-passage topics).
READING_TOPIC_OPTIONS = [
    "Daily life", "Work & jobs", "Travel", "Food & cooking", "Health", "Sport",
    "Science", "Technology", "Environment", "Culture & traditions",
    "News & current events", "History", "Money & shopping", "Education",
]
_MAX_TOPICS = 5

READING_COMPONENT_LABELS = {
    "reading.skim_gist": "Main idea and gist",
    "reading.scan_detail": "Finding details",
    "reading.infer_meaning": "Inference",
    "reading.vocab_in_context": "Vocabulary in context",
    "reading.authors_purpose": "Author purpose",
    "reading.implicit_attitude": "Tone and attitude",
}

READING_COMPONENT_HINTS = {
    "reading.skim_gist": "Read the first and last sentences, then choose the answer that covers the whole text.",
    "reading.scan_detail": "Underline keywords in the question, then find the matching detail in the passage.",
    "reading.infer_meaning": "Use clues from two nearby sentences, not only one word.",
    "reading.vocab_in_context": "Look before and after the word to guess its meaning from context.",
    "reading.authors_purpose": "Ask why the writer included this idea: to explain, persuade, compare, or warn.",
    "reading.implicit_attitude": "Notice opinion words and contrast words that show attitude.",
}

READING_LEVEL_DEFAULT_COMPONENT = {
    "A1": "reading.scan_detail",
    "A2": "reading.scan_detail",
    "B1": "reading.infer_meaning",
    "B2": "reading.authors_purpose",
    "C1": "reading.implicit_attitude",
    "C2": "reading.implicit_attitude",
}

READING_PROFILE_BASE = {
    "A1": {
        "reading.skim_gist": 40,
        "reading.scan_detail": 35,
        "reading.infer_meaning": 20,
        "reading.vocab_in_context": 30,
        "reading.authors_purpose": 15,
        "reading.implicit_attitude": 15,
    },
    "A2": {
        "reading.skim_gist": 52,
        "reading.scan_detail": 50,
        "reading.infer_meaning": 35,
        "reading.vocab_in_context": 42,
        "reading.authors_purpose": 25,
        "reading.implicit_attitude": 25,
    },
    "B1": {
        "reading.skim_gist": 64,
        "reading.scan_detail": 62,
        "reading.infer_meaning": 50,
        "reading.vocab_in_context": 55,
        "reading.authors_purpose": 42,
        "reading.implicit_attitude": 40,
    },
    "B2": {
        "reading.skim_gist": 74,
        "reading.scan_detail": 72,
        "reading.infer_meaning": 64,
        "reading.vocab_in_context": 66,
        "reading.authors_purpose": 58,
        "reading.implicit_attitude": 55,
    },
    "C1": {
        "reading.skim_gist": 82,
        "reading.scan_detail": 80,
        "reading.infer_meaning": 75,
        "reading.vocab_in_context": 76,
        "reading.authors_purpose": 72,
        "reading.implicit_attitude": 68,
    },
    "C2": {
        "reading.skim_gist": 88,
        "reading.scan_detail": 86,
        "reading.infer_meaning": 84,
        "reading.vocab_in_context": 84,
        "reading.authors_purpose": 82,
        "reading.implicit_attitude": 80,
    },
}

READING_WPM_TARGETS = {
    "A1": (60, 100),
    "A2": (80, 130),
    "B1": (100, 160),
    "B2": (120, 190),
    "C1": (140, 220),
    "C2": (160, 240),
}

READING_CHECKPOINT_REQUIREMENTS = {
    "required_passages": 5,
    "required_average": 75,
    "required_components": 3,
}

_SUMMARY_SYSTEM = (
    "You are an English reading-comprehension examiner for German learners. Judge whether the "
    "student's summary captures the passage's main ideas — reward understanding, not length or "
    "perfect grammar. Be encouraging but honest. English only. Return ONLY valid JSON."
)


def _parse_json_object(raw: str) -> dict | None:
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", (raw or "").strip())
    s, e = text.find("{"), text.rfind("}")
    if s == -1 or e == -1:
        return None
    try:
        data = json.loads(text[s : e + 1])
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


_EXPLAIN_SYSTEM = (
    "You are a friendly English teacher for German learners. Explain a sentence simply and briefly "
    "at the learner's level: what it means, and one note on its grammar/structure. English only. "
    "Return ONLY valid JSON."
)

# Whole-passage glossary is stable per content item — cache so tapping any word is instant.
_GLOSSARY_CACHE = TTLCache()
_GLOSSARY_TTL = 7 * 24 * 3600  # 7 days


async def reading_glossary(db: AsyncSession, *, student_id: int, content_id: int) -> dict:
    """Pre-compute a definition for every potentially-hard word in a passage in ONE call, so tapping
    any word is instant. Cached per content item. Returns {"glossary": {word_lower: {...}}}."""
    cached = _GLOSSARY_CACHE.get(content_id)
    if cached is not None:
        return {"glossary": cached}

    item, _ = await get_reading_lesson(db, student_id=student_id, content_id=content_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    passage = ((item.body_json or {}).get("passage") or "").strip()
    if not passage:
        return {"glossary": {}}

    # Build from the offline WordNet dictionary — free, instant, no quota. Covers the passage's
    # content words; tapping any of them is then instant even when Gemini is unavailable.
    from app.services.language_dictionary_service import lookup as dict_lookup

    glossary: dict[str, dict] = {}
    seen: set[str] = set()
    for raw_word in re.findall(r"[A-Za-z][A-Za-z'-]+", passage):
        key = raw_word.lower()
        if len(key) < 4 or key in seen:  # skip short/function-ish words + duplicates
            continue
        seen.add(key)
        entries = dict_lookup(raw_word, max_entries=1)
        if not entries:
            continue
        definition = (entries[0].get("definition") or "").strip()
        if not definition:
            continue
        glossary[key] = {
            "word": raw_word,
            "part_of_speech": str(entries[0].get("part_of_speech") or "").strip(),
            "definition": definition,
            "cefr_level": "",
        }
        if len(glossary) >= 60:
            break

    if glossary:
        _GLOSSARY_CACHE.set(content_id, glossary, _GLOSSARY_TTL)
    return {"glossary": glossary}


async def explain_sentence(*, sentence: str, level: str = "A2") -> dict:
    """On-demand AI explanation of a single sentence (meaning + a grammar note). Never raises."""
    sentence = (sentence or "").strip()
    if not sentence:
        return {"explanation": ""}
    prompt = (
        f'Explain this English sentence for a {level} learner: "{sentence}".'
        + level_calibration_line(level) + "\n"
        'Return ONLY JSON: {"meaning": short plain-English paraphrase, '
        '"grammar_note": one short note about the structure/grammar}.'
    )
    try:
        raw = await generate_llm_json(prompt, system=_EXPLAIN_SYSTEM, temperature=0.3, max_output_tokens=400)
        data = _parse_json_object(raw)
        if data:
            meaning = str(data.get("meaning") or "").strip()
            note = str(data.get("grammar_note") or "").strip()
            explanation = meaning + (f"\n\nGrammar: {note}" if note else "")
            return {"explanation": explanation.strip()}
    except Exception as exc:  # pragma: no cover - LLM variance
        logger.warning("explain_sentence failed: %s", exc)
    return {"explanation": "Explanation is temporarily unavailable. Please try again."}


async def grade_summary(db: AsyncSession, *, student_id: int, content_id: int, summary: str) -> dict:
    """Grade a student's free-text summary of a passage for comprehension (AI), feed the model."""
    item, _progress = await get_reading_lesson(db, student_id=student_id, content_id=content_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    passage = ((item.body_json or {}).get("passage") or "").strip()
    summary = (summary or "").strip()
    if not passage or len(summary) < 3:
        return {"score_percent": 0.0, "feedback": "Write a short summary first.", "covered_points": [], "missed_points": []}

    level = item.level.value if item.level else "A2"
    prompt = (
        f"PASSAGE (level {level}):\n{passage}\n\n"
        f"STUDENT SUMMARY:\n{summary}\n\n"
        "Assess how well the summary captures the passage's main ideas. Return ONLY JSON with EXACTLY: "
        "score_percent (0-100 integer for comprehension), "
        "feedback (1-2 encouraging English sentences), "
        "covered_points (list of main ideas the student GOT), "
        "missed_points (list of important ideas the student MISSED)."
    )
    score = 0.0
    result = {"score_percent": 0.0, "feedback": "", "covered_points": [], "missed_points": []}
    try:
        raw = await generate_llm_json(prompt, system=_SUMMARY_SYSTEM, temperature=0.3, max_output_tokens=700)
        data = _parse_json_object(raw)
        if data:
            score = max(0.0, min(100.0, float(data.get("score_percent") or 0)))
            result = {
                "score_percent": score,
                "feedback": str(data.get("feedback") or ""),
                "covered_points": [str(p) for p in (data.get("covered_points") or [])][:6],
                "missed_points": [str(p) for p in (data.get("missed_points") or [])][:6],
            }
    except Exception as exc:  # pragma: no cover - LLM variance
        logger.warning("Summary grading failed (content=%s): %s", content_id, exc)
        return {"score_percent": 0.0, "feedback": "The summary check is temporarily unavailable. Please try again.", "covered_points": [], "missed_points": []}

    # Feed the learner model: summarizing is reading comprehension at the passage's level.
    try:
        from app.services.language_learner_events import record_scored_practice

        language = await get_default_language(db)
        await record_scored_practice(
            db, student_id=student_id, language_id=language.id, skill=LanguageSkill.reading,
            level=item.level, score_percent=score, source="reading",
        )
    except Exception:  # never let evidence recording break the response
        pass
    return result


def nudge_reading_level(current: LanguageLevel | None, score_percent: float) -> LanguageLevel:
    """Adaptive step: strong pass -> harder, weak attempt -> easier, else stay (clamped A1..C2)."""
    # CEFR_RANK is 1..6 (A1..C2); clamp within that range — NOT 0..5, which crashed on RANK_CEFR[0]
    # for an A1 learner scoring < 40 and could never reach C2.
    rank = CEFR_RANK.get(current, 1) if current else 1
    if score_percent >= 85:
        rank = min(rank + 1, 6)
    elif score_percent < 40:
        rank = max(rank - 1, 1)
    return RANK_CEFR[rank]


def _level_str(level) -> str:
    value = getattr(level, "value", level)
    value = str(value or "A2").upper()
    return value if value in READING_LEVEL_DEFAULT_COMPONENT else "A2"


def _clamp_percent(value, default: int = 0) -> int:
    try:
        number = float(value)
    except Exception:
        number = float(default)
    return int(round(max(0.0, min(100.0, number))))


def _mini_lesson_for_component(component: str) -> dict:
    if component == "reading.skim_gist":
        return {
            "title": "Find the main idea",
            "steps": [
                "Read the title and first sentence.",
                "Ask what the whole passage is mostly about.",
                "Avoid answers that mention only one small detail.",
            ],
        }
    if component == "reading.scan_detail":
        return {
            "title": "Scan for details",
            "steps": [
                "Circle the keywords in the question.",
                "Find the same idea in the passage.",
                "Check names, numbers, places, and time words carefully.",
            ],
        }
    if component == "reading.infer_meaning":
        return {
            "title": "Make an inference",
            "steps": [
                "Use clues before and after the sentence.",
                "Choose what must be true, not what only sounds possible.",
                "Reject answers that add new information.",
            ],
        }
    if component == "reading.vocab_in_context":
        return {
            "title": "Guess from context",
            "steps": [
                "Look at the sentence before and after the word.",
                "Decide if the word is positive, negative, action, or object.",
                "Replace it with each option and see which one fits.",
            ],
        }
    if component == "reading.authors_purpose":
        return {
            "title": "Author purpose",
            "steps": [
                "Ask why the writer says this.",
                "Look for signal words like because, however, and therefore.",
                "Choose the option that explains the writer's goal.",
            ],
        }
    return {
        "title": "Tone and attitude",
        "steps": [
            "Look for opinion words.",
            "Notice contrast words like although and however.",
            "Choose the feeling or attitude supported by the text.",
        ],
    }


def _profile_rows_from_components(components: list[dict], *, level: str) -> list[dict]:
    base = dict(READING_PROFILE_BASE.get(level, READING_PROFILE_BASE["A2"]))
    evidence = {code: 0 for code in READING_COMPONENT_LABELS}
    for item in components:
        code = str(item.get("code") or "")
        if code not in base:
            continue
        base[code] = _clamp_percent(float(item.get("p_mastery") or 0.0) * 100.0)
        evidence[code] = int(item.get("evidence_count") or 0)
    rows = []
    for code, label in READING_COMPONENT_LABELS.items():
        score = _clamp_percent(base.get(code, 0))
        rows.append({
            "code": code,
            "label": label,
            "mastery_percent": score,
            "hint": READING_COMPONENT_HINTS.get(code, ""),
            "evidence_count": evidence.get(code, 0),
            "status": "strong" if score >= 75 else ("developing" if score >= 55 else "needs_practice"),
        })
    rows.sort(key=lambda row: (row["mastery_percent"], row["evidence_count"]))
    return rows


def _reading_plan_steps(*, focus: dict, level: str) -> list[dict]:
    focus_label = focus.get("label") or "Reading focus"
    return [
        {
            "order": 1,
            "status": "current",
            "title": f"Practice {focus_label.lower()}",
            "description": focus.get("hint") or "Use the strategy before answering.",
        },
        {
            "order": 2,
            "status": "active_reading",
            "title": "Read with evidence",
            "description": "After each answer, check the exact sentence that supports it.",
        },
        {
            "order": 3,
            "status": "summary",
            "title": "Summarise the passage",
            "description": "Write 1-2 sentences to prove you understood the main idea.",
        },
        {
            "order": 4,
            "status": "checkpoint",
            "title": f"Checkpoint after {level}",
            "description": "Unlock harder passages after stable comprehension across several focuses.",
        },
    ]


def _checkpoint_status(*, lessons_completed: int, scores: list[float], components: list[dict], level: str) -> dict:
    req = READING_CHECKPOINT_REQUIREMENTS
    average = round(sum(scores) / len(scores), 1) if scores else None
    covered = [c for c in components if int(c.get("mastery_percent") or 0) >= 60]
    passage_ratio = min(1.0, lessons_completed / max(1, req["required_passages"]))
    avg_ratio = min(1.0, (average or 0.0) / req["required_average"])
    component_ratio = min(1.0, len(covered) / max(1, req["required_components"]))
    progress_percent = _clamp_percent(((passage_ratio + avg_ratio + component_ratio) / 3.0) * 100)
    missing = []
    if lessons_completed < req["required_passages"]:
        missing.append(f"Complete {req['required_passages'] - lessons_completed} more reading passages.")
    if (average or 0.0) < req["required_average"]:
        missing.append(f"Reach an average comprehension of {req['required_average']}%.")
    if len(covered) < req["required_components"]:
        missing.append("Strengthen one more reading focus.")
    try:
        next_rank = min(CEFR_RANK.get(LanguageLevel(level), 1) + 1, 6)
        next_level = RANK_CEFR[next_rank].value if level != "C2" else None
    except Exception:
        next_level = "B1"
    return {
        "ready": not missing and level != "C2",
        "level": level,
        "next_level": next_level,
        "progress_percent": progress_percent,
        "lessons_completed": lessons_completed,
        "required_passages": req["required_passages"],
        "average_score_percent": average,
        "required_average": req["required_average"],
        "covered_components": [c["code"] for c in covered],
        "required_components": req["required_components"],
        "missing": missing,
    }


def _lesson_focus(item: LanguageContentItem, fallback_component: str | None = None) -> dict:
    level = _level_str(item.level)
    body = item.body_json or {}
    counts: dict[str, int] = {}
    for q in body.get("questions") or []:
        code = component_for_question(LanguageSkill.reading, qtype=q.get("type"), level=level)
        if code:
            counts[code] = counts.get(code, 0) + 1
    component = fallback_component or (max(counts, key=counts.get) if counts else READING_LEVEL_DEFAULT_COMPONENT.get(level))
    return {
        "target_component": component,
        "target_focus": READING_COMPONENT_LABELS.get(component, component),
        "practice_hint": READING_COMPONENT_HINTS.get(component, "Read carefully and use evidence from the passage."),
        "mini_lesson": _mini_lesson_for_component(component),
        "question_focus_counts": counts,
    }


async def _adaptive_level(db: AsyncSession, *, student_id: int, language_id: int) -> str:
    analytics = await db.get(LanguageAnalytics, {"student_id": student_id, "language_id": language_id})
    if analytics and analytics.reading_level:
        return analytics.reading_level.value
    return "A2"


async def _unseen_reading(
    db: AsyncSession, *, student_id: int, language_id: int, level: str, generated_only: bool = False,
    length: str = "", newest: bool = False, focus_component: str | None = None,
) -> LanguageContentItem | None:
    seen = select(LanguageReadingProgress.content_item_id).where(
        LanguageReadingProgress.student_id == student_id,
        LanguageReadingProgress.status == LanguageContentProgressStatus.completed,
    )
    q = select(LanguageContentItem).where(
        LanguageContentItem.language_id == language_id,
        LanguageContentItem.skill == LanguageSkill.reading,
        LanguageContentItem.content_type == "lesson",
        LanguageContentItem.level == LanguageLevel(level),
        LanguageContentItem.is_published.is_(True),
        LanguageContentItem.id.notin_(seen),
    )
    if generated_only:
        # AI-generated items carry source='ai_nightly' and the rich explanation/quote/type fields.
        q = q.where(LanguageContentItem.body_json["source"].astext == "ai_nightly")
    # Serve the requested length: short/long must match exactly; medium also matches untagged items.
    rl = LanguageContentItem.body_json["reading_length"].astext
    if length == "short":
        q = q.where(rl == "short")
    elif length == "long":
        q = q.where(rl == "long")
    elif length == "medium":
        q = q.where(or_(rl == "medium", rl.is_(None)))
    # newest=True serves the just-generated passage. Otherwise sample a small random pool and prefer
    # a passage whose question mix matches the learner's weakest reading component.
    q = q.order_by(LanguageContentItem.id.desc() if newest else func.random()).limit(1 if newest else 12)
    candidates = list((await db.execute(q)).scalars().all())
    if not candidates:
        return None
    if newest or not focus_component:
        return candidates[0]

    def _match_count(item: LanguageContentItem) -> int:
        item_level = _level_str(item.level)
        total = 0
        for question in (item.body_json or {}).get("questions") or []:
            code = component_for_question(LanguageSkill.reading, qtype=question.get("type"), level=item_level)
            if code == focus_component:
                total += 1
        return total

    return max(candidates, key=_match_count)


async def _profile(db: AsyncSession, *, student_id: int, language_id: int) -> LanguageStudentProfile | None:
    return (
        await db.execute(
            select(LanguageStudentProfile).where(
                LanguageStudentProfile.student_id == student_id,
                LanguageStudentProfile.language_id == language_id,
            )
        )
    ).scalar_one_or_none()


async def _next_focus_component(db: AsyncSession, *, student_id: int, language_id: int, level: str) -> str | None:
    from app.services.language_learner_model_service import LanguageLearnerModelService

    profile = await LanguageLearnerModelService(db).get_component_profile(
        student_id=student_id, language_id=language_id
    )
    reading_comps = [c for c in profile if c.get("skill") == "reading"]
    rows = _profile_rows_from_components(reading_comps, level=level)
    return str(rows[0].get("code")) if rows else READING_LEVEL_DEFAULT_COMPONENT.get(level)


async def get_reading_topics(db: AsyncSession, *, student_id: int) -> dict:
    """The curated topic options + the topics this learner has opted into."""
    language = await get_default_language(db)
    profile = await _profile(db, student_id=student_id, language_id=language.id)
    selected = list(((profile.preferences_json or {}) if profile else {}).get("reading_topics") or [])
    return {"options": READING_TOPIC_OPTIONS, "selected": selected}


async def set_reading_topics(db: AsyncSession, *, student_id: int, topics: list[str]) -> dict:
    """Persist the learner's reading interests (validated against the curated list, capped)."""
    language = await get_default_language(db)
    valid_lower = {t.lower(): t for t in READING_TOPIC_OPTIONS}
    selected: list[str] = []
    for t in topics or []:
        canon = valid_lower.get((t or "").strip().lower())
        if canon and canon not in selected:
            selected.append(canon)
        if len(selected) >= _MAX_TOPICS:
            break
    profile = await _profile(db, student_id=student_id, language_id=language.id)
    if profile is not None:
        prefs = dict(profile.preferences_json or {})
        prefs["reading_topics"] = selected
        profile.preferences_json = prefs  # reassign so SQLAlchemy tracks the JSONB change
    return {"options": READING_TOPIC_OPTIONS, "selected": selected}


async def reading_history(db: AsyncSession, *, student_id: int, limit: int = 30) -> list[dict]:
    """Passages the learner has completed — their reading library, newest first."""
    rows = (
        await db.execute(
            select(LanguageContentItem, LanguageReadingProgress)
            .join(LanguageReadingProgress, LanguageReadingProgress.content_item_id == LanguageContentItem.id)
            .where(
                LanguageReadingProgress.student_id == student_id,
                LanguageReadingProgress.status == LanguageContentProgressStatus.completed,
            )
            .order_by(LanguageReadingProgress.completed_at.desc().nullslast())
            .limit(limit)
        )
    ).all()
    return [
        {
            "id": item.id,
            "title": item.title,
            "level": item.level.value if item.level else None,
            "topic": (item.body_json or {}).get("topic") or item.title,
            "score_percent": prog.score_percent,
            "completed_at": prog.completed_at,
        }
        for item, prog in rows
    ]


async def reading_insights(db: AsyncSession, *, student_id: int) -> dict:
    """Reading analytics for the learner: WPM trend, comprehension, and per-skill strengths/gaps."""
    language = await get_default_language(db)
    rows = (
        await db.execute(
            select(LanguageActivityLog.payload_json, LanguageActivityLog.created_at)
            .where(
                LanguageActivityLog.student_id == student_id,
                LanguageActivityLog.language_id == language.id,
                LanguageActivityLog.event_type == "reading_lesson_completed",
            )
            .order_by(LanguageActivityLog.created_at.desc())
            .limit(20)
        )
    ).all()
    wpms: list[int] = []
    scores: list[float] = []
    for payload, _created in rows:
        p = payload or {}
        if isinstance(p.get("wpm"), (int, float)) and p["wpm"]:
            wpms.append(int(p["wpm"]))
        if isinstance(p.get("score_percent"), (int, float)):
            scores.append(float(p["score_percent"]))
    wpms.reverse()  # chronological for a trend line

    from app.services.language_learner_model_service import LanguageLearnerModelService

    profile = await LanguageLearnerModelService(db).get_component_profile(
        student_id=student_id, language_id=language.id
    )
    reading_comps = [c for c in profile if c.get("skill") == "reading"]
    analytics = await db.get(LanguageAnalytics, {"student_id": student_id, "language_id": language.id})
    level = _level_str(analytics.reading_level if analytics and analytics.reading_level else "A2")
    skill_breakdown = _profile_rows_from_components(reading_comps, level=level)
    next_focus = skill_breakdown[0] if skill_breakdown else {
        "code": READING_LEVEL_DEFAULT_COMPONENT.get(level, "reading.scan_detail"),
        "label": READING_COMPONENT_LABELS.get(READING_LEVEL_DEFAULT_COMPONENT.get(level, "reading.scan_detail")),
        "mastery_percent": 0,
        "hint": "Read carefully and use evidence from the passage.",
    }
    wpm_target = READING_WPM_TARGETS.get(level, READING_WPM_TARGETS["A2"])
    checkpoint = _checkpoint_status(
        lessons_completed=len(rows),
        scores=scores,
        components=skill_breakdown,
        level=level,
    )

    def _skill(c: dict) -> dict:
        return {"code": c["code"], "mastery": round((c.get("p_mastery") or 0.0) * 100)}

    weak = [_skill(c) for c in sorted(reading_comps, key=lambda c: c.get("p_mastery") or 0.0)[:3]]
    strong = [_skill(c) for c in sorted(reading_comps, key=lambda c: -(c.get("p_mastery") or 0.0))[:3]]
    return {
        "wpm_recent": wpms[-10:],
        "avg_wpm": round(sum(wpms) / len(wpms)) if wpms else None,
        "best_wpm": max(wpms) if wpms else None,
        "avg_comprehension": round(sum(scores) / len(scores), 1) if scores else None,
        "lessons_completed": len(rows),
        "weak_skills": weak,
        "strong_skills": strong,
        "reading_profile": {
            "level": level,
            "next_focus": next_focus,
            "skill_breakdown": skill_breakdown,
            "plan_steps": _reading_plan_steps(focus=next_focus, level=level),
            "checkpoint": checkpoint,
            "wpm_target_min": wpm_target[0],
            "wpm_target_max": wpm_target[1],
            "recommended_strategy": READING_COMPONENT_HINTS.get(str(next_focus.get("code") or ""), ""),
        },
    }


async def next_reading(db: AsyncSession, *, student_id: int, length: str = "") -> dict | None:
    """The next adaptive reading passage (stripped of answers), generating content if the bank is low.

    ``length`` (short|medium|long) lets the learner pick how long the generated passage is.
    """
    language = await get_default_language(db)
    level = await _adaptive_level(db, student_id=student_id, language_id=language.id)
    focus_component = await _next_focus_component(db, student_id=student_id, language_id=language.id, level=level)

    # Token-saving: serve an existing unseen AI passage first (free, instant). Generate ONLY when the
    # fresh-AI pool is exhausted — and even then, skip while the breaker is tripped (e.g. Gemini
    # credits depleted) so we don't waste calls. The seeded bank is the always-available fallback.
    item = await _unseen_reading(
        db, student_id=student_id, language_id=language.id, level=level, generated_only=True, length=length,
        focus_component=focus_component,
    )
    if item is None and can_generate():
        profile = await _profile(db, student_id=student_id, language_id=language.id)
        topics = ", ".join(((profile.preferences_json or {}) if profile else {}).get("reading_topics") or [])
        from app.services.language_adaptive_generation_service import build_adaptive_context

        adaptive_context = await build_adaptive_context(
            db, student_id=student_id, language_id=language.id, skill="reading"
        )
        try:
            made = await generate_and_store(
                db, language_id=language.id, skill="reading", level=level, count=_ON_DEMAND_BATCH,
                topics=topics, length=length, adaptive_context=adaptive_context,
            )
            if made:
                note_generation_success()
                await db.commit()  # persist generated passages (GET endpoint won't commit otherwise)
                item = await _unseen_reading(
                    db, student_id=student_id, language_id=language.id, level=level,
                    generated_only=True, length=length, newest=True,
                )
            else:
                note_generation_failure()  # nothing produced (quota/credits) — back off
        except Exception as exc:  # pragma: no cover - LLM variance
            logger.warning("On-demand reading generation failed (%s): %s", level, exc)
            note_generation_failure()
            await db.rollback()

    # Fallbacks: any unseen AI passage (ignore length), then the seeded bank (always works offline).
    if item is None:
        item = await _unseen_reading(
            db, student_id=student_id, language_id=language.id, level=level,
            generated_only=True, focus_component=focus_component,
        )
    if item is None:
        item = await _unseen_reading(
            db, student_id=student_id, language_id=language.id, level=level,
            focus_component=focus_component,
        )
    if item is None:
        return None

    body = lesson_body_for_student(item)
    focus = _lesson_focus(item)
    return {
        "id": item.id,
        "title": item.title,
        "level": item.level.value if item.level else level,
        "topic": (item.body_json or {}).get("topic") or item.title,
        "passage": body.get("passage") or "",
        "glossary": body.get("glossary") or [],
        "questions": body.get("questions") or [],
        **focus,
    }
