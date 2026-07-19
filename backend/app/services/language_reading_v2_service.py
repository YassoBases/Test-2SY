from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import logging
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.language.analytics import LanguageAnalytics
from app.models.language.enums import LanguageLevel
from app.models.language.reading_v2 import (
    LanguageReadingV2Attempt,
    LanguageReadingV2StageProgress,
    LanguageReadingV2StudentState,
)
from app.schemas.language_reading_v2 import (
    GeneratedReadingActivity,
    GenerationBlueprint,
    ReadingV2AttemptOut,
    ReadingV2HistoryOut,
    ReadingV2Mode,
    ReadingV2OverviewOut,
    ReadingV2PathOut,
    ReadingV2QuestionResultOut,
    ReadingV2StageOut,
    ReadingV2SubmitAttemptOut,
    ValidationIssue,
    ValidationResult,
)
from app.services.ai_service import generate_llm_json

CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
INTERNAL_STAGES = ["Beginner", "Intermediate", "Advanced"]
QUESTION_TYPES = ["mcq", "gap_fill", "true_false", "short_answer"]
PROMPT_VERSION = "reading_v2_r7_topic_diversity"
VALIDATOR_VERSION = "reading_v2_validator_r1"
MODEL_USED = "local_mock"
MIN_STAGE_EVIDENCE_ATTEMPTS = 6
MASTERY_THRESHOLD = 80.0
PRACTICE_PASS_THRESHOLD = 70.0
READINESS_PASS_THRESHOLD = 80.0
STAGE_MIN_PRACTICE_ATTEMPTS = 5
STAGE_MIN_UNIQUE_ACTIVITIES = 4
STAGE_MIN_ANSWERED_QUESTIONS = 12
STAGE_MIN_QUESTION_TYPES = 3
STAGE_MIN_CORE_SUBSKILL_QUESTIONS = 3
STAGE_RECENT_WINDOW = 5
STAGE_RECENT_AVERAGE_THRESHOLD = 80.0
STAGE_RECENT_MIN_ATTEMPT_SCORE = 70.0
STAGE_CORE_SUBSKILL_THRESHOLD = 70.0
STAGE_CORE_SUBSKILL_FAILURE_THRESHOLD = 60.0
STAGE_CORE_SUBSKILL_MAX_RECENT_FAILURES = 1
READINESS_MIN_ANSWERED_QUESTIONS = 12
READINESS_MIN_QUESTION_TYPE_SCORE = 60.0
READINESS_RETAKE_PRACTICE_ATTEMPTS = 3
AI_PROVIDER_NAME = "ai"
LOCAL_MOCK_PROVIDER_NAME = "local_mock"
_SHORT_ANSWER_STOPWORDS = {
    "a",
    "an",
    "and",
    "at",
    "by",
    "for",
    "from",
    "he",
    "her",
    "his",
    "i",
    "in",
    "is",
    "it",
    "its",
    "my",
    "of",
    "on",
    "or",
    "our",
    "she",
    "that",
    "the",
    "their",
    "they",
    "this",
    "to",
    "we",
    "with",
    "you",
    "your",
}
_SHORT_ANSWER_GENERIC_TOKENS = {
    "answer",
    "english",
    "learn",
    "learns",
    "passage",
    "says",
    "student",
    "students",
    "text",
}
_SHORT_ANSWER_INFLECTIONS = {
    "ate": "eat",
    "eats": "eat",
    "eat": "eat",
    "go": "go",
    "goes": "go",
    "going": "go",
    "help": "help",
    "helps": "help",
    "read": "read",
    "reads": "read",
    "rest": "rest",
    "rests": "rest",
    "study": "study",
    "studies": "study",
    "studying": "study",
}

logger = logging.getLogger(__name__)
settings = get_settings()

_WORD_RANGES: dict[str, dict[str, tuple[int, int]]] = {
    "A1": {"Beginner": (55, 80), "Intermediate": (75, 105), "Advanced": (95, 130)},
    "A2": {"Beginner": (120, 170), "Intermediate": (150, 210), "Advanced": (190, 260)},
    "B1": {"Beginner": (300, 400), "Intermediate": (380, 500), "Advanced": (480, 620)},
    "B2": {"Beginner": (600, 760), "Intermediate": (740, 920), "Advanced": (900, 1100)},
    "C1": {"Beginner": (1050, 1250), "Intermediate": (1200, 1450), "Advanced": (1400, 1650)},
    "C2": {"Beginner": (1550, 1800), "Intermediate": (1750, 2050), "Advanced": (2000, 2300)},
}

_SUBSKILLS_BY_STAGE = {
    "Beginner": ["skim_gist", "scan_detail", "literal_comprehension"],
    "Intermediate": ["skim_gist", "scan_detail", "vocab_in_context", "infer_meaning"],
    "Advanced": ["scan_detail", "vocab_in_context", "infer_meaning", "author_purpose"],
}

_GRAMMAR_BY_LEVEL = {
    "A1": ["present_simple", "basic_nouns", "basic_adjectives"],
    "A2": ["past_simple", "comparatives", "future_going_to"],
    "B1": ["present_perfect", "modals", "relative_clauses"],
    "B2": ["passive_voice", "conditionals", "reported_speech"],
    "C1": ["advanced_clause_linking", "nominalisation", "hedging"],
    "C2": ["nuanced_modality", "inversion", "rhetorical_structure"],
}

_VOCAB_BY_LEVEL = {
    "A1": ["daily_routines", "places", "family"],
    "A2": ["travel", "work", "health"],
    "B1": ["community", "education", "technology"],
    "B2": ["culture", "environment", "workplace"],
    "C1": ["policy", "research", "abstract_ideas"],
    "C2": ["critique", "specialized_discourse", "nuance"],
}

_A1_BEGINNER_TOPIC_ROTATION = [
    "family meal",
    "classroom object",
    "simple shopping trip",
    "pet care",
    "weekend morning",
    "park visit",
    "school bag",
    "birthday card",
    "simple house routine",
    "bus ride",
]

_A2_TOPIC_ROTATION = [
    "market visit",
    "lost item at a station",
    "simple travel plan",
    "doctor appointment",
    "work break",
    "neighborhood event",
    "library card",
    "weather plan",
    "sports practice",
    "cafe order",
]

_STUDY_ROUTINE_TERMS = {
    "daily study",
    "study routine",
    "english study",
    "reading routine",
    "school routine",
    "library",
    "new words",
    "study group",
}

_SENSITIVE_TERMS = {
    "suicide",
    "self-harm",
    "sexual",
    "graphic violence",
    "terrorism",
    "hate speech",
    "illegal drugs",
    "weapon instructions",
}

_BLANK_MARKER_RE = re.compile(r"_{2,}|\[[^\]]*blank[^\]]*\]|\(\s*blank\s*\)", re.IGNORECASE)


@dataclass(slots=True)
class ReadingV2GenerationOutcome:
    activity: dict[str, Any] | None
    validation: ValidationResult
    provider_name: str
    model_used: str
    prompt_version: str
    retry_count: int = 0
    prompt: dict[str, str] | None = None


def stage_rank(cefr_level: str | LanguageLevel, internal_stage: str) -> int:
    level = cefr_level.value if isinstance(cefr_level, LanguageLevel) else str(cefr_level)
    return CEFR_LEVELS.index(level) * len(INTERNAL_STAGES) + INTERNAL_STAGES.index(internal_stage)


def next_cefr_level(cefr_level: str | LanguageLevel) -> str | None:
    level = cefr_level.value if isinstance(cefr_level, LanguageLevel) else str(cefr_level)
    index = CEFR_LEVELS.index(level)
    return CEFR_LEVELS[index + 1] if index + 1 < len(CEFR_LEVELS) else None


def _enum_value(value: str | LanguageLevel | None) -> str | None:
    return value.value if isinstance(value, LanguageLevel) else value


def _sentence_complexity_for(cefr: str, stage: str) -> str:
    if cefr == "A1" and stage == "Beginner":
        return "very_short_simple_present_direct_sentences"
    if cefr == "A1":
        return "short_simple_sentences_with_basic_connectors"
    if cefr == "A2":
        return "short_clear_sentences_simple_present_and_simple_past"
    return f"{cefr.lower()}_{stage.lower()}_sentences"


def _vocabulary_difficulty_for(cefr: str, stage: str) -> str:
    if cefr == "A1" and stage == "Beginner":
        return "concrete_daily_words_no_abstract_vocabulary"
    if cefr == "A1":
        return "concrete_familiar_words_with_few_new_items"
    if cefr == "A2":
        return "familiar_concrete_words_with_basic_school_travel_work_topics"
    return f"{cefr.lower()}_{stage.lower()}_vocabulary"


async def get_or_create_student_state(
    db: AsyncSession, *, student_id: int, language_id: int
) -> LanguageReadingV2StudentState:
    result = await db.execute(
        select(LanguageReadingV2StudentState).where(
            LanguageReadingV2StudentState.student_id == student_id,
            LanguageReadingV2StudentState.language_id == language_id,
        )
    )
    state_row = result.scalar_one_or_none()
    if state_row:
        return state_row

    analytics = (
        await db.execute(
            select(LanguageAnalytics).where(
                LanguageAnalytics.student_id == student_id,
                LanguageAnalytics.language_id == language_id,
            )
        )
    ).scalar_one_or_none()
    initial_level = analytics.reading_level if analytics and analytics.reading_level else LanguageLevel.A1
    await db.execute(
        pg_insert(LanguageReadingV2StudentState)
        .values(
            student_id=student_id,
            language_id=language_id,
            current_cefr=initial_level,
            current_stage="Beginner",
            status="active",
            unlocked_rank=stage_rank(initial_level, "Beginner"),
            recent_mastery_json={},
        )
        .on_conflict_do_nothing(constraint="uq_language_reading_v2_student_state")
    )
    result = await db.execute(
        select(LanguageReadingV2StudentState).where(
            LanguageReadingV2StudentState.student_id == student_id,
            LanguageReadingV2StudentState.language_id == language_id,
        )
    )
    state_row = result.scalar_one()
    return state_row


def _dedupe_keep_order(values: list[str], *, limit: int = 12) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        clean = " ".join(str(value or "").strip().split())
        key = clean.lower()
        if not clean or key in seen:
            continue
        seen.add(key)
        out.append(clean)
        if len(out) >= limit:
            break
    return out


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _tagify(value: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", value.lower())).strip("_")


def _activity_topic_tags(activity: dict[str, Any], blueprint: GenerationBlueprint | None = None) -> list[str]:
    explicit = _as_str_list(activity.get("topic_tags"))
    if explicit:
        return _dedupe_keep_order([_tagify(item) for item in explicit if _tagify(item)], limit=6)
    metadata = activity.get("diversity_metadata") if isinstance(activity.get("diversity_metadata"), dict) else {}
    metadata_tags = _as_str_list(metadata.get("topic_tags"))
    if metadata_tags:
        return _dedupe_keep_order([_tagify(item) for item in metadata_tags if _tagify(item)], limit=6)
    topic_value = activity.get("topic") or (blueprint.topic if blueprint else "")
    topic = str(topic_value or "").strip()
    derived = [_tagify(topic)] if topic else []
    derived.extend(_tagify(tag) for tag in _as_str_list(activity.get("vocab_tags"))[:2])
    return _dedupe_keep_order([tag for tag in derived if tag], limit=6)


def _passage_summary(activity: dict[str, Any]) -> str:
    metadata = activity.get("diversity_metadata") if isinstance(activity.get("diversity_metadata"), dict) else {}
    summary = str(metadata.get("passage_summary") or "").strip()
    if summary:
        return summary[:240]
    passage = " ".join(str(activity.get("passage") or "").split())
    first_sentence = re.split(r"(?<=[.!?])\s+", passage, maxsplit=1)[0]
    words = first_sentence.split()
    return " ".join(words[:20]).strip()


def _extract_character_names(activity: dict[str, Any]) -> list[str]:
    metadata = activity.get("diversity_metadata") if isinstance(activity.get("diversity_metadata"), dict) else {}
    names = _as_str_list(metadata.get("character_names"))
    if names:
        return _dedupe_keep_order(names, limit=8)
    text = " ".join([str(activity.get("title") or ""), str(activity.get("passage") or "")])
    excluded = {
        "A1",
        "A2",
        "B1",
        "B2",
        "C1",
        "C2",
        "Beginner",
        "Intermediate",
        "Advanced",
        "English",
        "The",
        "This",
        "When",
        "After",
        "Before",
        "True",
        "False",
    }
    candidates = re.findall(r"\b[A-Z][a-z]{2,}\b", text)
    return _dedupe_keep_order([name for name in candidates if name not in excluded], limit=8)


def _question_stems(activity: dict[str, Any]) -> list[str]:
    stems = []
    for question in activity.get("questions") or []:
        if isinstance(question, dict):
            stem = str(question.get("stem") or "").strip()
            if stem:
                stems.append(stem)
    return _dedupe_keep_order(stems, limit=10)


async def _recent_generation_context(
    db: AsyncSession, *, student_id: int, language_id: int, cefr_level: str, internal_stage: str, limit: int = 6
) -> dict[str, Any]:
    rows = (
        await db.execute(
            select(LanguageReadingV2Attempt)
            .where(
                LanguageReadingV2Attempt.student_id == student_id,
                LanguageReadingV2Attempt.language_id == language_id,
                LanguageReadingV2Attempt.cefr_level == LanguageLevel(cefr_level),
                LanguageReadingV2Attempt.internal_stage == internal_stage,
                LanguageReadingV2Attempt.status.in_(["ready", "submitted"]),
            )
            .order_by(LanguageReadingV2Attempt.created_at.desc(), LanguageReadingV2Attempt.id.desc())
            .limit(limit)
        )
    ).scalars().all()
    activities = [row.generated_activity_json for row in rows if isinstance(row.generated_activity_json, dict)]
    topic_tag_sets = [_activity_topic_tags(activity) for activity in activities]
    return {
        "recent_titles": _dedupe_keep_order([str(activity.get("title") or "") for activity in activities], limit=limit),
        "recent_topics": _dedupe_keep_order([str(activity.get("topic") or "") for activity in activities], limit=limit),
        "recent_topic_tags": [tags for tags in topic_tag_sets if tags][:limit],
        "recent_passage_summaries": _dedupe_keep_order([_passage_summary(activity) for activity in activities], limit=limit),
        "recent_character_names": _dedupe_keep_order(
            [name for activity in activities for name in _extract_character_names(activity)], limit=12
        ),
        "recent_question_stems": _dedupe_keep_order(
            [stem for activity in activities for stem in _question_stems(activity)], limit=12
        ),
    }


def _preferred_topic_rotation(cefr: str, stage: str) -> list[str]:
    if cefr == "A1" and stage == "Beginner":
        return list(_A1_BEGINNER_TOPIC_ROTATION)
    if cefr in {"A1", "A2"}:
        return list(_A1_BEGINNER_TOPIC_ROTATION if cefr == "A1" else _A2_TOPIC_ROTATION)
    return []


def _subskill_record(name: str, stats: dict[str, Any] | None) -> dict[str, Any]:
    stats = stats or {}
    return {
        "name": name,
        "correct": float(stats.get("correct") or 0.0),
        "total": float(stats.get("total") or 0.0),
        "score_percent": float(stats.get("score_percent") or 0.0),
        "required_questions": STAGE_MIN_CORE_SUBSKILL_QUESTIONS,
    }


def _classify_core_subskills(subskills: dict[str, dict[str, float]], core_subskills: list[str]) -> dict[str, Any]:
    records = [_subskill_record(name, subskills.get(name)) for name in core_subskills]
    under_sampled = [record for record in records if record["total"] < STAGE_MIN_CORE_SUBSKILL_QUESTIONS]
    weak = [
        record
        for record in records
        if record["total"] >= STAGE_MIN_CORE_SUBSKILL_QUESTIONS
        and record["score_percent"] < STAGE_CORE_SUBSKILL_THRESHOLD
    ]
    return {
        "records": records,
        "under_sampled": under_sampled,
        "weak": weak,
        "scores": {record["name"]: record["score_percent"] for record in records},
    }


def _target_subskills_from_evidence(evidence: dict[str, Any]) -> tuple[list[str], str | None]:
    under_sampled = [item["name"] for item in evidence.get("under_sampled_subskills") or [] if item.get("name")]
    weak = [item["name"] for item in evidence.get("weak_subskills") or [] if item.get("name")]
    targets = _dedupe_keep_order([*under_sampled, *weak], limit=4)
    if under_sampled and weak:
        return targets, "Prioritize under-sampled and weak core reading subskills."
    if under_sampled:
        return targets, "Prioritize core reading subskills that need more evidence."
    if weak:
        return targets, "Prioritize core reading subskills with enough evidence but low scores."
    return [], None


def _prioritized_subskills_for_questions(blueprint: GenerationBlueprint) -> list[str]:
    return _dedupe_keep_order([*blueprint.target_subskills, *blueprint.reading_subskills], limit=12) or list(
        blueprint.reading_subskills
    )


async def build_generation_blueprint(
    db: AsyncSession, *, student_id: int, language_id: int, mode: ReadingV2Mode = "practice"
) -> GenerationBlueprint:
    state_row = await get_or_create_student_state(db, student_id=student_id, language_id=language_id)
    cefr = _enum_value(state_row.current_cefr) or "A1"
    stage = state_row.current_stage
    word_min, word_max = _WORD_RANGES[cefr][stage]
    question_count = 12 if mode == "readiness" else 4
    question_types = (QUESTION_TYPES * ((question_count // len(QUESTION_TYPES)) + 1))[:question_count]
    target_next = next_cefr_level(cefr) if mode == "readiness" else None
    topic = "everyday learning habits" if mode == "practice" else f"{target_next or cefr} readiness"
    recent_context = await _recent_generation_context(
        db,
        student_id=student_id,
        language_id=language_id,
        cefr_level=cefr,
        internal_stage=stage,
    )
    evidence = await evaluate_stage_evidence(
        db,
        student_id=student_id,
        language_id=language_id,
        cefr_level=cefr,
        internal_stage=stage,
    )
    target_subskills, target_reason = _target_subskills_from_evidence(evidence)

    return GenerationBlueprint(
        cefr_level=cefr,
        internal_stage=stage,
        mode=mode,
        word_count_min=word_min,
        word_count_max=word_max,
        sentence_complexity=_sentence_complexity_for(cefr, stage),
        vocabulary_difficulty=_vocabulary_difficulty_for(cefr, stage),
        target_vocab_tags=_VOCAB_BY_LEVEL[cefr],
        required_vocab_items=[],
        target_grammar_tags=_GRAMMAR_BY_LEVEL[cefr],
        banned_above_level_grammar=[
            tag
            for level in CEFR_LEVELS[CEFR_LEVELS.index(cefr) + 1 :]
            for tag in _GRAMMAR_BY_LEVEL[level]
        ],
        reading_subskills=_SUBSKILLS_BY_STAGE[stage],
        question_types=question_types,
        student_interest=None,
        topic=topic,
        difficulty_score=min(100.0, 8.0 + stage_rank(cefr, stage) * 5.0 + (8.0 if mode == "readiness" else 0.0)),
        inference_depth={"Beginner": "direct", "Intermediate": "mixed", "Advanced": "indirect"}[stage],
        number_of_questions=question_count,
        safety_topic_restrictions=sorted(_SENSITIVE_TERMS),
        prompt_version=PROMPT_VERSION,
        known_vocab_items=[],
        weak_vocab_items=[],
        grammar_mastery_profile={},
        vocab_review_due_items=[],
        preferred_topic_rotation=_preferred_topic_rotation(cefr, stage),
        target_subskills=target_subskills,
        under_sampled_subskills=[item["name"] for item in evidence.get("under_sampled_subskills") or []],
        weak_subskills=[item["name"] for item in evidence.get("weak_subskills") or []],
        subskill_targeting_reason=target_reason,
        **recent_context,
    )


def generate_reading_activity_from_blueprint(blueprint: GenerationBlueprint) -> GeneratedReadingActivity:
    sentences = [
        "Mira joins a small study group after school because she wants to read with more confidence.",
        "The group chooses one short article, marks useful words, and writes simple notes in the margin.",
        "At first, Mira reads slowly, but she checks the title, pictures, and first sentence before reading every detail.",
        "This helps her understand the main idea before she looks for names, times, and reasons.",
        "When a word is new, she reads the words around it and guesses the meaning before using a dictionary.",
        "By the end of the week, she can explain the article to a friend and answer questions with clear evidence.",
    ]
    words: list[str] = []
    index = 0
    while len(words) < blueprint.word_count_min:
        words.extend(sentences[index % len(sentences)].split())
        index += 1
    passage = " ".join(words[: blueprint.word_count_min])
    questions = []
    answer_specs = [
        (
            "mcq",
            "skim_gist",
            "What is the main idea of the passage?",
            {
                "correct_choice_id": "a",
            },
            [
                {"id": "a", "text": "Mira learns helpful ways to read more confidently."},
                {"id": "b", "text": "Mira decides to stop reading after school."},
                {"id": "c", "text": "Mira writes a story about a city."},
            ],
        ),
        (
            "gap_fill",
            "vocab_in_context",
            "The group writes simple notes in the ____.",
            {"accepted_answers": ["margin"]},
            [],
        ),
        (
            "true_false",
            "scan_detail",
            "Mira checks context before using a dictionary.",
            {"correct": True},
            [],
        ),
        (
            "short_answer",
            "literal_comprehension",
            "Name one strategy Mira uses before reading every detail.",
            {
                "accepted_answers": ["checks the title", "looks at pictures", "reads the first sentence"],
                "required_key_terms": ["title"],
            },
            [],
        ),
    ]
    answer_specs_by_type = {spec[0]: spec for spec in answer_specs}
    prioritized_subskills = _prioritized_subskills_for_questions(blueprint)
    for i, question_type in enumerate(blueprint.question_types, start=1):
        spec = answer_specs_by_type.get(question_type)
        if spec:
            q_type, subskill, stem, answer_key, choices = spec
        else:
            q_type = question_type
            stem = f"Answer this {question_type.replace('_', ' ')} question about Mira's reading routine."
            answer_key = _fallback_answer_key(question_type)
            choices = _fallback_choices(question_type)
        sentence_with_blank = _fallback_gap_fill_sentence() if q_type == "gap_fill" and not _has_exactly_one_blank(stem) else None
        if q_type == "gap_fill" and _has_exactly_one_blank(stem):
            sentence_with_blank = stem
        subskill = prioritized_subskills[(i - 1) % len(prioritized_subskills)]
        questions.append(
            {
                "id": f"q{i}",
                "type": q_type,
                "subskill": subskill,
                "stem": stem,
                "sentence_with_blank": sentence_with_blank,
                "choices": choices,
                "answer_key": answer_key,
                "explanation": "The passage directly supports this answer.",
                "evidence_quote": "This helps her understand the main idea.",
            }
        )

    return GeneratedReadingActivity(
        cefr_level=blueprint.cefr_level,
        internal_stage=blueprint.internal_stage,
        title=f"{blueprint.cefr_level} {blueprint.internal_stage} Reading Routine",
        passage=passage,
        word_count=len(passage.split()),
        grammar_tags=blueprint.target_grammar_tags[:3],
        vocab_tags=blueprint.target_vocab_tags[:3],
        skill_tags=blueprint.reading_subskills,
        difficulty_score=blueprint.difficulty_score,
        topic=blueprint.topic,
        topic_tags=_activity_topic_tags({"topic": blueprint.topic, "vocab_tags": blueprint.target_vocab_tags}, blueprint),
        questions=questions,
        safety_tags=["education", "low_risk"],
        diversity_metadata={
            "topic_tags": _activity_topic_tags({"topic": blueprint.topic, "vocab_tags": blueprint.target_vocab_tags}, blueprint),
            "character_names": ["Mira"],
            "passage_summary": _passage_summary({"passage": passage}),
            "recent_titles_considered": blueprint.recent_titles,
            "recent_topics_considered": blueprint.recent_topics,
        },
        validation_metadata={"provider": LOCAL_MOCK_PROVIDER_NAME, "prompt_version": blueprint.prompt_version, "retry_count": 0},
    )


def _fallback_answer_key(question_type: str) -> dict[str, Any]:
    if question_type == "mcq":
        return {"correct_choice_id": "a"}
    if question_type == "true_false":
        return {"correct": True}
    if question_type == "gap_fill":
        return {"accepted_answers": ["first sentence"]}
    return {"accepted_answers": ["title"], "required_key_terms": ["title"]}


def _fallback_choices(question_type: str) -> list[dict[str, str]]:
    if question_type != "mcq":
        return []
    return [
        {"id": "a", "text": "A helpful reading strategy."},
        {"id": "b", "text": "A cooking instruction."},
        {"id": "c", "text": "A weather report."},
    ]


def _fallback_gap_fill_sentence() -> str:
    return "Before reading every detail, Mira checks the title, pictures, and ____."


def _blank_marker_count(value: str | None) -> int:
    return len(_BLANK_MARKER_RE.findall(str(value or "")))


def _has_exactly_one_blank(value: str | None) -> bool:
    return _blank_marker_count(value) == 1


def _gap_fill_display_sentence(question: Any) -> str:
    for field in ("sentence_with_blank", "display_sentence", "blank_prompt"):
        value = getattr(question, field, None)
        if value is not None and str(value).strip():
            return str(value)
    stem = getattr(question, "stem", None)
    if _has_exactly_one_blank(stem):
        return str(stem)
    return ""


def _sentence_word_counts(text: str) -> list[int]:
    counts: list[int] = []
    for sentence in re.split(r"[.!?]+", text):
        words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", sentence)
        if words:
            counts.append(len(words))
    return counts


def _validate_level_readability(passage: str, blueprint: GenerationBlueprint, issues: list[ValidationIssue]) -> None:
    sentence_counts = _sentence_word_counts(passage)
    max_sentence_words = max(sentence_counts or [0])
    if blueprint.cefr_level == "A1" and blueprint.internal_stage == "Beginner":
        if max_sentence_words > 18:
            issues.append(
                ValidationIssue(
                    code="a1_beginner_sentence_too_long",
                    message="A1 Beginner passages need very short, clear sentences",
                )
            )
        abstract_terms = {"hypothesis", "policy", "phenomenon", "rhetorical", "nuance", "ideology"}
        if any(re.search(rf"\b{re.escape(term)}\b", passage, flags=re.IGNORECASE) for term in abstract_terms):
            issues.append(
                ValidationIssue(
                    code="a1_beginner_abstract_wording",
                    message="A1 Beginner passages need concrete daily vocabulary",
                )
            )
    elif blueprint.cefr_level == "A2" and max_sentence_words > 24:
        issues.append(
            ValidationIssue(
                code="a2_sentence_too_long",
                message="A2 passages need short, clear sentences",
            )
        )


def _token_set(value: str) -> set[str]:
    return {token for token in _normalize_text(value).split() if token}


def _title_similarity_score(left: str, right: str) -> float:
    left_tokens = _token_set(left)
    right_tokens = _token_set(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _contains_study_routine_pattern(value: str) -> bool:
    normalized = _normalize_text(value)
    return any(_normalize_text(term) in normalized for term in _STUDY_ROUTINE_TERMS)


def _diversity_warnings(parsed: GeneratedReadingActivity, blueprint: GenerationBlueprint) -> list[ValidationIssue]:
    warnings: list[ValidationIssue] = []
    title = parsed.title.strip()
    for recent_title in blueprint.recent_titles:
        score = _title_similarity_score(title, recent_title)
        if _normalize_text(title) == _normalize_text(recent_title) or score >= 0.6:
            warnings.append(
                ValidationIssue(
                    code="repeated_or_similar_title",
                    message="Generated title is identical or highly similar to a recent Reading V2 title",
                )
            )
            break

    current_tags = set(_activity_topic_tags(parsed.model_dump(), blueprint))
    repeated_tag_sets = 0
    for recent_tags in blueprint.recent_topic_tags:
        if current_tags and current_tags == set(_tagify(tag) for tag in recent_tags if _tagify(tag)):
            repeated_tag_sets += 1
    if repeated_tag_sets:
        warnings.append(
            ValidationIssue(
                code="repeated_topic_tags",
                message="Generated topic tags repeat recent Reading V2 topic tags",
            )
        )

    recent_context_text = " ".join(
        [*blueprint.recent_titles, *blueprint.recent_topics, *blueprint.recent_passage_summaries]
    )
    generated_context_text = " ".join([parsed.title, parsed.topic, parsed.passage])
    if _contains_study_routine_pattern(generated_context_text) and _contains_study_routine_pattern(recent_context_text):
        warnings.append(
            ValidationIssue(
                code="repeated_study_routine_pattern",
                message="Generated passage appears to repeat a recent school/study/library routine pattern",
            )
        )

    return warnings


def validate_generated_activity(activity: dict[str, Any] | GeneratedReadingActivity, blueprint: GenerationBlueprint) -> ValidationResult:
    issues: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []
    raw = activity.model_dump() if isinstance(activity, GeneratedReadingActivity) else activity
    parsed: GeneratedReadingActivity | None = None
    try:
        parsed = GeneratedReadingActivity.model_validate(raw)
    except Exception as exc:
        issues.append(ValidationIssue(code="invalid_shape", message=str(exc)))
        return ValidationResult(valid=False, issues=issues)

    if parsed.cefr_level != blueprint.cefr_level:
        issues.append(ValidationIssue(code="cefr_mismatch", message="Activity CEFR does not match blueprint"))
    if parsed.internal_stage != blueprint.internal_stage:
        issues.append(ValidationIssue(code="stage_mismatch", message="Activity stage does not match blueprint"))
    if not parsed.passage.strip():
        issues.append(ValidationIssue(code="empty_passage", message="Passage must not be empty"))
    actual_word_count = len(parsed.passage.split())
    if actual_word_count < blueprint.word_count_min or actual_word_count > blueprint.word_count_max:
        issues.append(ValidationIssue(code="word_count_out_of_range", message="Passage word count is outside blueprint range"))
    _validate_level_readability(parsed.passage, blueprint, issues)
    if not parsed.grammar_tags:
        issues.append(ValidationIssue(code="missing_grammar_tags", message="Activity must include grammar tags"))
    if not parsed.vocab_tags:
        issues.append(ValidationIssue(code="missing_vocab_tags", message="Activity must include vocabulary tags"))
    if not set(blueprint.target_grammar_tags).intersection(parsed.grammar_tags):
        issues.append(ValidationIssue(code="grammar_tags_not_targeted", message="Activity grammar tags do not match blueprint"))
    if not set(blueprint.target_vocab_tags).intersection(parsed.vocab_tags):
        issues.append(ValidationIssue(code="vocab_tags_not_targeted", message="Activity vocabulary tags do not match blueprint"))
    if len(parsed.questions) != blueprint.number_of_questions:
        issues.append(ValidationIssue(code="question_count_mismatch", message="Activity question count does not match blueprint"))
    if _contains_sensitive_topic(parsed):
        issues.append(ValidationIssue(code="unsafe_topic", message="Activity contains a restricted topic"))
    warnings.extend(_diversity_warnings(parsed, blueprint))

    for question in parsed.questions:
        q_type = question.type
        answer_key = question.answer_key or {}
        if q_type not in QUESTION_TYPES:
            issues.append(
                ValidationIssue(code="unsupported_question_type", message="Unsupported question type", question_id=question.id)
            )
            continue
        if not answer_key:
            issues.append(ValidationIssue(code="missing_answer_key", message="Question is missing an answer key", question_id=question.id))
            continue
        text_for_leak_check = question.stem
        if q_type == "gap_fill":
            text_for_leak_check = f"{question.stem} {_gap_fill_display_sentence(question)}"
        if _leaks_answer(text_for_leak_check, answer_key, question.choices, q_type):
            issues.append(ValidationIssue(code="answer_leakage", message="Question stem leaks the answer", question_id=question.id))
        if q_type == "mcq":
            _validate_mcq(question, answer_key, issues)
        elif q_type == "gap_fill":
            if not answer_key.get("accepted_answers"):
                issues.append(ValidationIssue(code="missing_gap_fill_answers", message="Gap Fill needs accepted answers", question_id=question.id))
            gap_sentence = _gap_fill_display_sentence(question)
            if not gap_sentence.strip():
                issues.append(
                    ValidationIssue(
                        code="missing_gap_fill_sentence",
                        message="Gap Fill needs a student-facing sentence with a blank",
                        question_id=question.id,
                    )
                )
            elif not _has_exactly_one_blank(gap_sentence):
                issues.append(
                    ValidationIssue(
                        code="invalid_gap_fill_blank",
                        message="Gap Fill sentence must contain exactly one blank marker",
                        question_id=question.id,
                    )
                )
        elif q_type == "true_false":
            if not isinstance(answer_key.get("correct"), bool):
                issues.append(ValidationIssue(code="invalid_true_false_key", message="True/False answer must be boolean", question_id=question.id))
        elif q_type == "short_answer":
            if not answer_key.get("accepted_answers") and not answer_key.get("required_key_terms"):
                issues.append(
                    ValidationIssue(
                        code="missing_short_answer_key",
                        message="Short Answer needs accepted answers or required key terms",
                        question_id=question.id,
                    )
                )

    return ValidationResult(valid=not issues, issues=issues, warnings=warnings)


def select_reading_v2_generation_provider() -> str:
    provider = (settings.READING_V2_GENERATION_PROVIDER or LOCAL_MOCK_PROVIDER_NAME).strip().lower()
    return provider if provider in {LOCAL_MOCK_PROVIDER_NAME, AI_PROVIDER_NAME} else LOCAL_MOCK_PROVIDER_NAME


def reading_v2_ai_model_name() -> str:
    return (settings.READING_V2_AI_MODEL or settings.CLAUDE_MODEL or "claude-sonnet-5").strip()


def reading_v2_generation_prompt(blueprint: GenerationBlueprint, *, validation_errors: list[str] | None = None) -> dict[str, str]:
    schema = {
        "title": "string",
        "passage": "string",
        "word_count": "integer",
        "cefr_level": blueprint.cefr_level,
        "internal_stage": blueprint.internal_stage,
        "grammar_tags": ["string"],
        "vocab_tags": ["string"],
        "skill_tags": ["string"],
        "difficulty_score": "number",
        "topic": "string",
        "target_subskills": ["string"],
        "subskill_targeting_reason": "string or null",
        "topic_tags": ["short_topic_tag"],
        "safety_tags": ["string"],
        "diversity_metadata": {
            "topic_tags": ["short_topic_tag"],
            "character_names": ["names used in the passage"],
            "passage_summary": "one short sentence summary",
            "anti_repetition_notes": "brief note about how this differs from recent activities",
        },
        "validation_metadata": {"notes": "optional object"},
        "questions": [
            {
                "id": "q1",
                "type": "mcq|true_false|gap_fill|short_answer",
                "subskill": "one of reading_subskills",
                "stem": "string",
                "sentence_with_blank": "required for gap_fill: a natural sentence with exactly one ____ blank marker; null otherwise",
                "display_sentence": "optional alias for sentence_with_blank",
                "blank_prompt": "optional alias for sentence_with_blank",
                "choices": [{"id": "a", "text": "string"}],
                "answer_key": {
                    "correct_choice_id": "for mcq only",
                    "correct": "boolean for true_false only",
                    "accepted_answers": ["for gap_fill or short_answer"],
                    "required_key_terms": ["for short_answer when useful"],
                },
                "explanation": "string",
                "evidence_quote": "short quote from passage when applicable",
            }
        ],
    }
    blueprint_payload = blueprint.model_dump()
    diversity_block = ""
    if (
        blueprint.recent_titles
        or blueprint.recent_topics
        or blueprint.recent_topic_tags
        or blueprint.recent_character_names
        or blueprint.recent_question_stems
    ):
        diversity_block = f"""

Recent generated activity context for this same student/language/stage:
- Recent titles: {json.dumps(blueprint.recent_titles, ensure_ascii=False)}
- Recent topics: {json.dumps(blueprint.recent_topics, ensure_ascii=False)}
- Recent topic_tags: {json.dumps(blueprint.recent_topic_tags, ensure_ascii=False)}
- Recent passage summaries: {json.dumps(blueprint.recent_passage_summaries, ensure_ascii=False)}
- Recent character names: {json.dumps(blueprint.recent_character_names, ensure_ascii=False)}
- Recent question stems: {json.dumps(blueprint.recent_question_stems, ensure_ascii=False)}
"""
    topic_rotation_block = ""
    if blueprint.preferred_topic_rotation:
        topic_rotation_block = (
            "\nAllowed simple topic rotation for this level/stage. Prefer one that is not present in recent context:\n"
            + json.dumps(blueprint.preferred_topic_rotation, ensure_ascii=False)
        )
    repair_block = ""
    if validation_errors:
        repair_block = (
            "\nValidation errors from the previous generated JSON. Regenerate or repair the JSON so all issues are fixed:\n"
            + json.dumps(validation_errors, ensure_ascii=False)
        )

    system = """You generate English reading practice activities for CEFR learners.
The Generation Blueprint is authoritative. Do not change level, stage, word count range, question count, question types, tags, safety limits, or deterministic answer-key rules.
Return valid JSON only. Do not use markdown fences, commentary, or extra prose outside JSON.
Avoid unsafe, sensitive, graphic, sexual, hateful, self-harm, extremist, illegal, or weapon-instruction topics."""

    user = f"""Create one personalized Reading Practice V2 activity from this strict Generation Blueprint.

Generation Blueprint JSON:
{json.dumps(blueprint_payload, ensure_ascii=False, indent=2)}
{diversity_block}
{topic_rotation_block}

Must include these control fields from the blueprint:
- cefr_level
- internal_stage
- word_count_min / word_count_max
- sentence_complexity
- vocabulary_difficulty
- target_vocab_tags
- required_vocab_items
- target_grammar_tags
- banned_above_level_grammar
- reading_subskills
- question_types
- student_interest or topic
- difficulty_score
- inference_depth
- number_of_questions
- safety_topic_restrictions
- recent_titles / recent_topics / recent_topic_tags / recent_passage_summaries / recent_character_names / recent_question_stems
- preferred_topic_rotation
- target_subskills / under_sampled_subskills / weak_subskills / subskill_targeting_reason

Hard requirements:
- Passage must be between {blueprint.word_count_min} and {blueprint.word_count_max} words.
- Activity cefr_level must be {blueprint.cefr_level}.
- Activity internal_stage must be {blueprint.internal_stage}.
- For A1 Beginner, use 55-80 words, very short sentences, simple present, concrete daily vocabulary, and direct literal questions.
- For A1/A2, avoid abstract wording, long dense sentences, complex clauses, and above-level grammar.
- For A1/A2, vary the setting and situation while preserving the same CEFR/stage simplicity.
- Do not repeat recent topics, titles, topic_tags, character names, or passage patterns from the recent context.
- Do not reuse the same character names listed in recent_character_names.
- Do not generate another school/study/library/new-words routine if recent attempts already used that pattern.
- If recent activities are about daily English study, choose a different simple situation such as a family meal, classroom object, simple shopping trip, pet care, weekend morning, park visit, school bag, birthday card, simple house routine, or bus ride.
- Include at least one target grammar tag and one target vocabulary tag.
- Include topic_tags and diversity_metadata.topic_tags.
- Include diversity_metadata.character_names and diversity_metadata.passage_summary.
- Include diversity_metadata.anti_repetition_notes explaining how this activity differs from recent attempts.
- If target_subskills is not empty, include questions for those subskills early in the activity while keeping the exact requested question type order.
- Under-sampled subskills need more evidence, not harder questions. For Skim Gist at A1 Beginner, use direct main-idea prompts such as "What is the passage mainly about?", "What is the best title?", or "What is the main idea?"
- Weak subskills need focused practice at the same CEFR/stage difficulty, not above-level text.
- Create exactly {blueprint.number_of_questions} questions in this exact order: {blueprint.question_types}.
- MCQ questions need at least three plausible choices and answer_key.correct_choice_id.
- True/False questions need answer_key.correct as a boolean.
- Gap Fill questions need deterministic answer_key.accepted_answers and sentence_with_blank with exactly one visible ____ marker.
- Gap Fill sentence_with_blank must be a meaningful sentence grounded in the passage and must not reveal the accepted answer.
- Short Answer questions must be scoreable without AI using accepted_answers or required_key_terms.
- Short Answer answer keys must include common natural variants when the answer is a short phrase. For example, if the passage says the student studies English at home, include accepted_answers like "home", "at home", "the student studies at home", and "she studies at home", or required_key_terms like "home".
- For Short Answer, include required_key_terms as base-form meaning concepts when useful, not only one full sentence. For example, if the answer is "eat a snack and rest", include accepted_answers like "eat a snack and rest", "they eat a snack and rest", "eat a snack", and required_key_terms like "eat snack" and "rest" so deterministic scoring can accept "the family eats a snack and rests".
- Include common A1 natural variants for simple verbs: eat/eats, rest/rests, study/studies, read/reads, go/goes, help/helps.
- Question stems must not reveal answer_key values.
- Explanations and evidence_quote must be grounded in the passage.
- Do not include any answer keys inside passage text, title, or stems in a way that leaks answers.

Return JSON matching this schema:
{json.dumps(schema, ensure_ascii=False, indent=2)}
{repair_block}"""
    return {"system": system, "user": user}


def _validation_issue_messages(validation: ValidationResult) -> list[str]:
    return [
        f"{issue.code}{f' ({issue.question_id})' if issue.question_id else ''}: {issue.message}"
        for issue in validation.issues
    ]


def parse_ai_activity_json(raw: str) -> dict[str, Any]:
    cleaned = (raw or "").strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start < 0 or end <= start:
            raise
        parsed = json.loads(cleaned[start:end])
    if not isinstance(parsed, dict):
        raise ValueError("AI generation returned JSON that is not an object")
    return parsed


async def generate_activity_with_local_mock_provider(blueprint: GenerationBlueprint) -> ReadingV2GenerationOutcome:
    activity = generate_reading_activity_from_blueprint(blueprint)
    validation = validate_generated_activity(activity, blueprint)
    return ReadingV2GenerationOutcome(
        activity=activity.model_dump(),
        validation=validation,
        provider_name=LOCAL_MOCK_PROVIDER_NAME,
        model_used=MODEL_USED,
        prompt_version=blueprint.prompt_version,
        retry_count=0,
    )


async def generate_activity_with_ai_provider(blueprint: GenerationBlueprint) -> ReadingV2GenerationOutcome:
    max_retries = max(0, int(settings.READING_V2_AI_MAX_RETRIES or 0))
    max_attempts = max_retries + 1
    model_name = reading_v2_ai_model_name()
    last_activity: dict[str, Any] | None = None
    last_validation = ValidationResult(
        valid=False,
        issues=[ValidationIssue(code="generation_not_attempted", message="AI generation did not run")],
    )
    validation_errors: list[str] | None = None
    last_prompt: dict[str, str] | None = None

    for attempt_index in range(max_attempts):
        last_prompt = reading_v2_generation_prompt(blueprint, validation_errors=validation_errors)
        try:
            raw = await generate_llm_json(
                last_prompt["user"],
                system=last_prompt["system"],
                temperature=0.4,
                max_output_tokens=settings.READING_V2_AI_MAX_OUTPUT_TOKENS,
                model_name=model_name,
            )
            last_activity = parse_ai_activity_json(raw)
        except Exception as exc:
            logger.warning("Reading V2 AI generation parse failed: %s", exc)
            last_activity = None
            last_validation = ValidationResult(
                valid=False,
                issues=[ValidationIssue(code="invalid_json", message="AI returned invalid JSON")],
            )
            validation_errors = _validation_issue_messages(last_validation)
            continue

        last_activity.setdefault("validation_metadata", {})
        if isinstance(last_activity["validation_metadata"], dict):
            last_activity["validation_metadata"].update(
                {
                    "provider": AI_PROVIDER_NAME,
                    "model_used": model_name,
                    "prompt_version": blueprint.prompt_version,
                    "retry_count": attempt_index,
                }
            )
        topic_tags = _activity_topic_tags(last_activity, blueprint)
        if not _as_str_list(last_activity.get("topic_tags")):
            last_activity["topic_tags"] = topic_tags
        diversity_metadata = last_activity.setdefault("diversity_metadata", {})
        if isinstance(diversity_metadata, dict):
            diversity_metadata.setdefault("topic_tags", topic_tags)
            diversity_metadata.setdefault("character_names", _extract_character_names(last_activity))
            diversity_metadata.setdefault("passage_summary", _passage_summary(last_activity))
            diversity_metadata.setdefault("recent_titles_considered", blueprint.recent_titles)
            diversity_metadata.setdefault("recent_topics_considered", blueprint.recent_topics)
        else:
            last_activity["diversity_metadata"] = {
                "topic_tags": topic_tags,
                "character_names": _extract_character_names(last_activity),
                "passage_summary": _passage_summary(last_activity),
                "recent_titles_considered": blueprint.recent_titles,
                "recent_topics_considered": blueprint.recent_topics,
            }
        last_validation = validate_generated_activity(last_activity, blueprint)
        if last_validation.valid:
            return ReadingV2GenerationOutcome(
                activity=last_activity,
                validation=last_validation,
                provider_name=AI_PROVIDER_NAME,
                model_used=model_name,
                prompt_version=blueprint.prompt_version,
                retry_count=attempt_index,
                prompt=last_prompt,
            )
        validation_errors = _validation_issue_messages(last_validation)

    return ReadingV2GenerationOutcome(
        activity=last_activity,
        validation=last_validation,
        provider_name=AI_PROVIDER_NAME,
        model_used=model_name,
        prompt_version=blueprint.prompt_version,
        retry_count=max_retries,
        prompt=last_prompt,
    )


async def generate_activity_for_blueprint(blueprint: GenerationBlueprint) -> ReadingV2GenerationOutcome:
    provider = select_reading_v2_generation_provider()
    if provider == AI_PROVIDER_NAME:
        return await generate_activity_with_ai_provider(blueprint)
    return await generate_activity_with_local_mock_provider(blueprint)


def _contains_sensitive_topic(activity: GeneratedReadingActivity) -> bool:
    text = " ".join([activity.title, activity.topic, activity.passage]).lower()
    return any(term in text for term in _SENSITIVE_TERMS)


def _leaks_answer(stem: str, answer_key: dict[str, Any], choices: list[Any], question_type: str) -> bool:
    lower_stem = stem.lower()
    leaked_terms: list[str] = []
    if question_type == "mcq":
        correct_id = str(answer_key.get("correct_choice_id", ""))
        for choice in choices:
            choice_id = getattr(choice, "id", None) or choice.get("id")
            choice_text = getattr(choice, "text", None) or choice.get("text", "")
            if choice_id == correct_id and len(choice_text) >= 8:
                leaked_terms.append(choice_text)
    elif question_type in {"gap_fill", "short_answer"}:
        leaked_terms.extend(str(v) for v in answer_key.get("accepted_answers") or [])
        leaked_terms.extend(str(v) for v in answer_key.get("required_key_terms") or [])
    return any(term and term.lower() in lower_stem for term in leaked_terms)


def _validate_mcq(question: Any, answer_key: dict[str, Any], issues: list[ValidationIssue]) -> None:
    choices = question.choices or []
    choice_ids = [choice.id for choice in choices]
    choice_texts = [choice.text.strip().lower() for choice in choices]
    if len(choices) < 3:
        issues.append(ValidationIssue(code="missing_mcq_distractors", message="MCQ needs at least 3 choices", question_id=question.id))
    if len(set(choice_texts)) != len(choice_texts):
        issues.append(ValidationIssue(code="duplicate_mcq_choices", message="MCQ choices must be distinct", question_id=question.id))
    if answer_key.get("correct_choice_id") not in choice_ids:
        issues.append(ValidationIssue(code="invalid_mcq_key", message="MCQ answer key must point to a choice", question_id=question.id))


def strip_answer_keys(activity: dict[str, Any] | GeneratedReadingActivity | None) -> dict[str, Any]:
    if not activity:
        return {}
    payload = activity.model_dump() if isinstance(activity, GeneratedReadingActivity) else dict(activity)
    stripped_questions = []
    for question in payload.get("questions") or []:
        safe_question = {key: value for key, value in question.items() if key != "answer_key"}
        stripped_questions.append(safe_question)
    payload["questions"] = stripped_questions
    return payload


def score_generated_activity(
    activity: dict[str, Any] | GeneratedReadingActivity, answers: dict[str, Any]
) -> tuple[float, list[ReadingV2QuestionResultOut]]:
    parsed = activity if isinstance(activity, GeneratedReadingActivity) else GeneratedReadingActivity.model_validate(activity)
    results: list[ReadingV2QuestionResultOut] = []
    correct_count = 0
    for question in parsed.questions:
        answer = answers.get(question.id)
        is_correct = _score_question(question.type, question.answer_key or {}, answer)
        if is_correct:
            correct_count += 1
        results.append(
            ReadingV2QuestionResultOut(
                question_id=question.id,
                question_type=question.type,
                subskill=question.subskill,
                correct=is_correct,
                score=1.0 if is_correct else 0.0,
                student_answer=_student_answer_summary(question, answer),
                expected_answer=_expected_answer_summary(question),
                explanation=question.explanation,
            )
        )
    score_percent = round((correct_count / len(parsed.questions)) * 100.0, 2) if parsed.questions else 0.0
    return score_percent, results


def _score_question(question_type: str, answer_key: dict[str, Any], answer: Any) -> bool:
    candidate = _answer_candidate(answer)
    if question_type == "mcq":
        return str(candidate or "") == str(answer_key.get("correct_choice_id") or "")
    if question_type == "true_false":
        return _as_bool(candidate) is answer_key.get("correct")
    if question_type == "gap_fill":
        normalized = _normalize_text(str(candidate or ""))
        return normalized in {_normalize_text(str(item)) for item in answer_key.get("accepted_answers") or []}
    if question_type == "short_answer":
        if _short_answer_matches(str(candidate or ""), answer_key):
            return True
    return False


def _answer_candidate(answer: Any) -> Any:
    if isinstance(answer, dict):
        candidate = answer.get("choice_id")
        if candidate is None:
            candidate = answer.get("value")
        if candidate is None:
            candidate = answer.get("answer")
        return candidate
    return answer


def _short_answer_matches(candidate: str, answer_key: dict[str, Any]) -> bool:
    normalized = _normalize_text(candidate)
    if not normalized:
        return False

    accepted = [_normalize_text(str(item)) for item in answer_key.get("accepted_answers") or [] if str(item).strip()]
    if normalized in set(accepted):
        return True

    candidate_tokens = _meaningful_short_answer_tokens(normalized)
    for accepted_answer in accepted:
        accepted_tokens = _meaningful_short_answer_tokens(accepted_answer)
        if _meaningful_tokens_match(candidate_tokens, accepted_tokens):
            return True
        if accepted_answer and (f" {normalized} " in f" {accepted_answer} " or f" {accepted_answer} " in f" {normalized} "):
            if candidate_tokens and any(token in accepted_tokens for token in candidate_tokens):
                return True

    required = [_normalize_text(str(item)) for item in answer_key.get("required_key_terms") or [] if str(item).strip()]
    if required:
        return all(
            _required_term_matches(candidate_tokens, _meaningful_short_answer_tokens(term))
            for term in required
        )
    return False


def _canonical_short_answer_token(token: str) -> str:
    clean = token.lower().strip()
    if clean in _SHORT_ANSWER_INFLECTIONS:
        return _SHORT_ANSWER_INFLECTIONS[clean]
    if clean.endswith("ies") and len(clean) > 4:
        return clean[:-3] + "y"
    if clean.endswith("es") and len(clean) > 4 and clean[-3] in {"s", "x", "z", "h", "o"}:
        return clean[:-2]
    if clean.endswith("s") and len(clean) > 3 and not clean.endswith(("ss", "us", "is")):
        return clean[:-1]
    return clean


def _meaningful_short_answer_tokens(value: str) -> set[str]:
    tokens = set(re.findall(r"[a-z0-9]+", value.lower()))
    return {
        _canonical_short_answer_token(token)
        for token in tokens
        if token not in _SHORT_ANSWER_STOPWORDS
        and token not in _SHORT_ANSWER_GENERIC_TOKENS
        and len(token) > 1
    }


def _meaningful_tokens_match(candidate_tokens: set[str], expected_tokens: set[str]) -> bool:
    if not candidate_tokens or not expected_tokens:
        return False
    return expected_tokens.issubset(candidate_tokens)


def _required_term_matches(candidate_tokens: set[str], required_tokens: set[str]) -> bool:
    if not candidate_tokens or not required_tokens:
        return False
    return required_tokens.issubset(candidate_tokens)


def _student_answer_summary(question: Any, answer: Any) -> str:
    candidate = _answer_candidate(answer)
    if question.type == "mcq":
        for choice in question.choices or []:
            if choice.id == candidate:
                return choice.text
    if question.type == "true_false":
        boolean = _as_bool(candidate)
        if boolean is not None:
            return "True" if boolean else "False"
    return str(candidate or "").strip()


def _expected_answer_summary(question: Any) -> str:
    answer_key = question.answer_key or {}
    if question.type == "mcq":
        correct_id = str(answer_key.get("correct_choice_id") or "")
        for choice in question.choices or []:
            if choice.id == correct_id:
                return choice.text
    if question.type == "true_false":
        correct = answer_key.get("correct")
        if isinstance(correct, bool):
            return "True" if correct else "False"
    accepted = [str(item).strip() for item in answer_key.get("accepted_answers") or [] if str(item).strip()]
    if accepted:
        return " / ".join(accepted[:3])
    required = [str(item).strip() for item in answer_key.get("required_key_terms") or [] if str(item).strip()]
    if required:
        return "Must include: " + ", ".join(required[:3])
    return ""


def _as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "t", "yes", "y", "1"}:
            return True
        if normalized in {"false", "f", "no", "n", "0"}:
            return False
    return None


def _normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", "", " ".join(value.lower().split())).strip()


async def create_reading_v2_attempt(
    db: AsyncSession, *, student_id: int, language_id: int, mode: ReadingV2Mode = "practice"
) -> ReadingV2AttemptOut:
    state_row = await get_or_create_student_state(db, student_id=student_id, language_id=language_id)
    if mode == "readiness":
        readiness_gate = await build_readiness_gate(db, state_row=state_row)
        if not readiness_gate["available"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "Reading readiness test is not available yet.",
                    "reason": readiness_gate["blocked_reason"],
                    "readiness": readiness_gate,
                },
            )
    blueprint = await build_generation_blueprint(db, student_id=student_id, language_id=language_id, mode=mode)
    outcome = await generate_activity_for_blueprint(blueprint)
    activity = outcome.activity
    validation = outcome.validation
    target_next = next_cefr_level(blueprint.cefr_level) if mode == "readiness" else None
    blueprint_snapshot = blueprint.model_dump()
    blueprint_snapshot["generation_provider"] = outcome.provider_name
    blueprint_snapshot["generation_retry_count"] = outcome.retry_count
    if outcome.prompt:
        blueprint_snapshot["generation_prompt"] = outcome.prompt
    validation_snapshot = validation.model_dump()
    validation_snapshot["generation_provider"] = outcome.provider_name
    validation_snapshot["generation_retry_count"] = outcome.retry_count
    validation_snapshot["model_used"] = outcome.model_used
    attempt = LanguageReadingV2Attempt(
        student_id=student_id,
        language_id=language_id,
        cefr_level=LanguageLevel(blueprint.cefr_level),
        internal_stage=blueprint.internal_stage,
        mode=mode,
        status="ready" if validation.valid else "generation_failed",
        target_next_cefr=LanguageLevel(target_next) if target_next else None,
        generation_blueprint_json=blueprint_snapshot,
        generated_activity_json=activity,
        validation_result_json=validation_snapshot,
        model_used=outcome.model_used,
        prompt_version=outcome.prompt_version,
        validator_version=validation.validator_version,
    )
    db.add(attempt)
    await db.flush()
    if not validation.valid:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not create a valid reading activity. Please try again.",
        )
    return attempt_to_out(attempt)


def attempt_to_out(attempt: LanguageReadingV2Attempt) -> ReadingV2AttemptOut:
    validation = ValidationResult.model_validate(attempt.validation_result_json)
    return ReadingV2AttemptOut(
        attempt_id=attempt.id,
        mode=attempt.mode,
        status=attempt.status,
        cefr_level=_enum_value(attempt.cefr_level) or "A1",
        internal_stage=attempt.internal_stage,
        activity=strip_answer_keys(attempt.generated_activity_json),
        validation=validation,
        created_at=attempt.created_at,
        submitted_at=attempt.submitted_at,
        score_percent=attempt.score_percent,
    )


async def build_reading_v2_overview(db: AsyncSession, *, student_id: int, language_id: int) -> ReadingV2OverviewOut:
    state_row = await get_or_create_student_state(db, student_id=student_id, language_id=language_id)
    cefr = _enum_value(state_row.current_cefr) or "A1"
    stage = state_row.current_stage
    evidence = await evaluate_stage_evidence(
        db,
        student_id=student_id,
        language_id=language_id,
        cefr_level=cefr,
        internal_stage=stage,
    )
    readiness_gate = await build_readiness_gate(db, state_row=state_row, current_stage_evidence=evidence)
    mastery = dict(state_row.recent_mastery_json or {})
    mastery["current_stage_evidence"] = evidence
    mastery["readiness"] = readiness_gate
    return ReadingV2OverviewOut(
        student_id=student_id,
        language_id=language_id,
        current_cefr=cefr,
        current_stage=stage,
        status=state_row.status,
        readiness_target_level=_enum_value(state_row.readiness_target_level),
        readiness_available=readiness_gate["available"],
        readiness_blocked_reason=readiness_gate["blocked_reason"],
        recent_mastery=mastery,
        next_action="readiness" if readiness_gate["available"] else "practice",
    )


async def build_reading_v2_path(db: AsyncSession, *, student_id: int, language_id: int) -> ReadingV2PathOut:
    state_row = await get_or_create_student_state(db, student_id=student_id, language_id=language_id)
    result = await db.execute(
        select(LanguageReadingV2StageProgress).where(
            LanguageReadingV2StageProgress.student_id == student_id,
            LanguageReadingV2StageProgress.language_id == language_id,
        )
    )
    progress_by_rank = {
        stage_rank(row.cefr_level, row.internal_stage): row
        for row in result.scalars().all()
    }
    stages: list[ReadingV2StageOut] = []
    current_rank = stage_rank(state_row.current_cefr, state_row.current_stage)
    for cefr in CEFR_LEVELS:
        for stage in INTERNAL_STAGES:
            rank = stage_rank(cefr, stage)
            progress = progress_by_rank.get(rank)
            row_status = (
                progress.status
                if progress
                else ("current" if rank == current_rank else "locked" if rank > state_row.unlocked_rank else "unlocked")
            )
            stages.append(
                ReadingV2StageOut(
                    cefr_level=cefr,
                    internal_stage=stage,
                    rank=rank,
                    status=row_status,
                    attempts_completed=progress.attempts_completed if progress else 0,
                    mastery_score=round(progress.mastery_score, 2) if progress else 0.0,
                    recent_mastery=(
                        _stage_path_summary(progress=progress, rank=rank, state_row=state_row, current_rank=current_rank)
                    ),
                )
            )
    return ReadingV2PathOut(student_id=student_id, language_id=language_id, stages=stages)


async def submit_reading_v2_attempt(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int,
    attempt_id: int,
    answers: dict[str, Any],
    duration_seconds: int | None = None,
) -> ReadingV2SubmitAttemptOut:
    attempt = (
        await db.execute(
            select(LanguageReadingV2Attempt).where(
                LanguageReadingV2Attempt.id == attempt_id,
                LanguageReadingV2Attempt.student_id == student_id,
                LanguageReadingV2Attempt.language_id == language_id,
            )
        )
    ).scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reading attempt not found")
    if attempt.status != "ready":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Reading attempt is not open for submission")

    score_percent, question_results = score_generated_activity(attempt.generated_activity_json or {}, answers)
    attempt.score_percent = score_percent
    attempt.question_results_json = [result.model_dump() for result in question_results]
    attempt.duration_seconds = duration_seconds
    attempt.submitted_at = datetime.now(timezone.utc)
    attempt.status = "submitted"

    evidence_update = await record_attempt_evidence(db, attempt=attempt, question_results=question_results)
    state_row = await get_or_create_student_state(db, student_id=student_id, language_id=language_id)
    passed = bool(evidence_update.get("passed", score_percent >= PRACTICE_PASS_THRESHOLD))
    return ReadingV2SubmitAttemptOut(
        attempt_id=attempt.id,
        score_percent=score_percent,
        passed=passed,
        question_results=question_results,
        state={
            "current_cefr": _enum_value(state_row.current_cefr),
            "current_stage": state_row.current_stage,
            "status": state_row.status,
            "recent_mastery": state_row.recent_mastery_json or {},
        },
        next_action=evidence_update.get("next_action") or _next_action(attempt, passed),
    )


async def record_attempt_evidence(
    db: AsyncSession, *, attempt: LanguageReadingV2Attempt, question_results: list[ReadingV2QuestionResultOut]
) -> dict[str, Any]:
    if attempt.mode == "readiness":
        return await record_readiness_evidence(db, attempt=attempt, question_results=question_results)

    progress = (
        await db.execute(
            select(LanguageReadingV2StageProgress).where(
                LanguageReadingV2StageProgress.student_id == attempt.student_id,
                LanguageReadingV2StageProgress.language_id == attempt.language_id,
                LanguageReadingV2StageProgress.cefr_level == attempt.cefr_level,
                LanguageReadingV2StageProgress.internal_stage == attempt.internal_stage,
            )
        )
    ).scalar_one_or_none()
    if not progress:
        progress = LanguageReadingV2StageProgress(
            student_id=attempt.student_id,
            language_id=attempt.language_id,
            cefr_level=attempt.cefr_level,
            internal_stage=attempt.internal_stage,
            status="current",
            attempts_completed=0,
            mastery_score=0.0,
            subskill_mastery_json={},
            question_type_mastery_json={},
            recent_attempt_ids_json=[],
        )
        db.add(progress)
        await db.flush()

    old_attempts = int(progress.attempts_completed or 0)
    progress.attempts_completed = old_attempts + 1
    recent_ids = list(progress.recent_attempt_ids_json or [])
    recent_ids.append(attempt.id)
    progress.recent_attempt_ids_json = recent_ids[-10:]

    state_row = await get_or_create_student_state(db, student_id=attempt.student_id, language_id=attempt.language_id)
    evidence = await evaluate_stage_evidence(
        db,
        student_id=attempt.student_id,
        language_id=attempt.language_id,
        cefr_level=_enum_value(attempt.cefr_level) or "A1",
        internal_stage=attempt.internal_stage,
    )
    progress.mastery_score = float(evidence["recent_average_score"] or 0.0)
    progress.subskill_mastery_json = evidence["subskills"]
    progress.question_type_mastery_json = evidence["question_types"]
    progress.status = "mastered" if progress.status == "mastered" else (
        "current"
        if stage_rank(progress.cefr_level, progress.internal_stage)
        == stage_rank(state_row.current_cefr, state_row.current_stage)
        else progress.status
    )

    state_row.recent_mastery_json = _merge_recent_mastery(
        state_row.recent_mastery_json,
        {
            "current_stage_evidence": evidence,
            "attempts_completed": progress.attempts_completed,
            "mastery_score": progress.mastery_score,
            "subskills": progress.subskill_mastery_json,
            "question_types": progress.question_type_mastery_json,
            "evidence_sufficient": evidence["mastered"],
        },
    )
    if evidence["mastered"]:
        await apply_stage_mastery(db, state_row=state_row, progress=progress)
        state_row.recent_mastery_json = _merge_recent_mastery(
            state_row.recent_mastery_json,
            {"current_stage_evidence": evidence, "readiness": await build_readiness_gate(db, state_row=state_row)},
        )
    else:
        state_row.recent_mastery_json = _merge_recent_mastery(
            state_row.recent_mastery_json,
            {"readiness": await build_readiness_gate(db, state_row=state_row, current_stage_evidence=evidence)},
        )
    return {"passed": float(attempt.score_percent or 0.0) >= PRACTICE_PASS_THRESHOLD, "next_action": "continue_practice", "evidence": evidence}


async def evaluate_stage_evidence(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int,
    cefr_level: str | LanguageLevel,
    internal_stage: str,
) -> dict[str, Any]:
    attempts = await submitted_practice_attempts_for_stage(
        db,
        student_id=student_id,
        language_id=language_id,
        cefr_level=cefr_level,
        internal_stage=internal_stage,
    )
    recent = attempts[-STAGE_RECENT_WINDOW:]
    all_results = [result for row in attempts for result in _attempt_question_results(row)]
    recent_results = [result for row in recent for result in _attempt_question_results(row)]
    question_types = sorted({result.question_type for result in all_results})
    unique_signatures = {_activity_signature(row.generated_activity_json) for row in attempts}
    unique_signatures.discard("")
    unique_count = len(unique_signatures)
    recent_scores = [float(row.score_percent or 0.0) for row in recent]
    recent_average = round(sum(recent_scores) / len(recent_scores), 2) if recent_scores else 0.0
    recent_lowest = min(recent_scores) if recent_scores else 0.0
    subskills = _aggregate_results(recent_results, "subskill")
    question_type_mastery = _aggregate_results(recent_results, "question_type")
    core_subskills = _SUBSKILLS_BY_STAGE[internal_stage]
    core_evidence = _classify_core_subskills(subskills, core_subskills)
    core_scores = core_evidence["scores"]
    under_sampled_subskills = core_evidence["under_sampled"]
    weak_subskills = core_evidence["weak"]
    core_failure_counts = _recent_core_subskill_failure_counts(recent, core_subskills)
    requirements = {
        "min_5_submitted_practice_attempts": len(attempts) >= STAGE_MIN_PRACTICE_ATTEMPTS,
        "min_4_unique_generated_activities": unique_count >= STAGE_MIN_UNIQUE_ACTIVITIES if unique_signatures else True,
        "min_12_answered_questions": len(all_results) >= STAGE_MIN_ANSWERED_QUESTIONS,
        "min_3_question_types": len(question_types) >= STAGE_MIN_QUESTION_TYPES,
        "recent_5_average_at_least_80": len(recent) >= STAGE_RECENT_WINDOW and recent_average >= STAGE_RECENT_AVERAGE_THRESHOLD,
        "no_recent_attempt_below_70": len(recent) >= STAGE_RECENT_WINDOW and all(score >= STAGE_RECENT_MIN_ATTEMPT_SCORE for score in recent_scores),
        "each_core_subskill_has_min_evidence": not under_sampled_subskills,
        "each_core_subskill_at_least_70": not weak_subskills,
        "no_core_subskill_two_recent_failures_below_60": all(
            count <= STAGE_CORE_SUBSKILL_MAX_RECENT_FAILURES for count in core_failure_counts.values()
        ),
    }
    blocking_reasons = [name for name, passed in requirements.items() if not passed]
    return {
        "mastered": not blocking_reasons,
        "requirements": requirements,
        "blocking_reasons": blocking_reasons,
        "attempts_submitted": len(attempts),
        "unique_generated_activities": unique_count,
        "total_answered_questions": len(all_results),
        "question_types_represented": question_types,
        "recent_attempt_ids": [row.id for row in recent],
        "recent_average_score": recent_average,
        "recent_lowest_score": recent_lowest,
        "core_subskills": core_subskills,
        "core_subskill_scores": core_scores,
        "core_subskill_min_questions": STAGE_MIN_CORE_SUBSKILL_QUESTIONS,
        "core_subskill_evidence": core_evidence["records"],
        "under_sampled_subskills": under_sampled_subskills,
        "weak_subskills": weak_subskills,
        "core_subskill_failures_below_60_last_5": core_failure_counts,
        "subskills": subskills,
        "question_types": question_type_mastery,
    }


async def submitted_practice_attempts_for_stage(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int,
    cefr_level: str | LanguageLevel,
    internal_stage: str,
) -> list[LanguageReadingV2Attempt]:
    result = await db.execute(
        select(LanguageReadingV2Attempt)
        .where(
            LanguageReadingV2Attempt.student_id == student_id,
            LanguageReadingV2Attempt.language_id == language_id,
            LanguageReadingV2Attempt.cefr_level == LanguageLevel(_enum_value(cefr_level) or "A1"),
            LanguageReadingV2Attempt.internal_stage == internal_stage,
            LanguageReadingV2Attempt.mode == "practice",
            LanguageReadingV2Attempt.status == "submitted",
        )
        .order_by(LanguageReadingV2Attempt.id.asc())
    )
    return list(result.scalars().all())


def _attempt_question_results(attempt: LanguageReadingV2Attempt) -> list[ReadingV2QuestionResultOut]:
    return [ReadingV2QuestionResultOut.model_validate(item) for item in (attempt.question_results_json or [])]


def _activity_signature(activity: dict[str, Any] | None) -> str:
    if not activity:
        return ""
    source = " ".join(str(activity.get(key) or "") for key in ("title", "passage")).strip()
    if not source:
        return ""
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _recent_core_subskill_failure_counts(
    attempts: list[LanguageReadingV2Attempt], core_subskills: list[str]
) -> dict[str, int]:
    counts = {subskill: 0 for subskill in core_subskills}
    totals = {subskill: 0.0 for subskill in core_subskills}
    for attempt in attempts:
        subskill_scores = _aggregate_results(_attempt_question_results(attempt), "subskill")
        for subskill in core_subskills:
            totals[subskill] += float((subskill_scores.get(subskill) or {}).get("total") or 0.0)
    for attempt in attempts:
        subskill_scores = _aggregate_results(_attempt_question_results(attempt), "subskill")
        for subskill in core_subskills:
            if totals[subskill] < STAGE_MIN_CORE_SUBSKILL_QUESTIONS or subskill not in subskill_scores:
                continue
            score = float((subskill_scores.get(subskill) or {}).get("score_percent") or 0.0)
            if score < STAGE_CORE_SUBSKILL_FAILURE_THRESHOLD:
                counts[subskill] += 1
    return counts


async def apply_stage_mastery(
    db: AsyncSession, *, state_row: LanguageReadingV2StudentState, progress: LanguageReadingV2StageProgress
) -> None:
    progress.status = "mastered"
    progress.mastered_at = progress.mastered_at or datetime.now(timezone.utc)
    cefr = _enum_value(progress.cefr_level) or "A1"
    current_rank = stage_rank(cefr, progress.internal_stage)
    state_row.unlocked_rank = max(int(state_row.unlocked_rank or 0), current_rank)
    if progress.internal_stage != "Advanced":
        next_stage = INTERNAL_STAGES[INTERNAL_STAGES.index(progress.internal_stage) + 1]
        next_rank = stage_rank(cefr, next_stage)
        state_row.current_stage = next_stage
        state_row.unlocked_rank = max(int(state_row.unlocked_rank or 0), next_rank)
        state_row.readiness_target_level = None
        next_progress = await get_or_create_stage_progress(
            db,
            student_id=progress.student_id,
            language_id=progress.language_id,
            cefr_level=cefr,
            internal_stage=next_stage,
        )
        if next_progress.status != "mastered":
            next_progress.status = "current"
        return

    target = next_cefr_level(cefr)
    if not target:
        state_row.status = "mastered"
        state_row.readiness_target_level = None
        return
    state_row.current_stage = "Advanced"
    state_row.readiness_target_level = LanguageLevel(target)


async def get_or_create_stage_progress(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int,
    cefr_level: str | LanguageLevel,
    internal_stage: str,
) -> LanguageReadingV2StageProgress:
    level = LanguageLevel(_enum_value(cefr_level) or "A1")
    progress = (
        await db.execute(
            select(LanguageReadingV2StageProgress).where(
                LanguageReadingV2StageProgress.student_id == student_id,
                LanguageReadingV2StageProgress.language_id == language_id,
                LanguageReadingV2StageProgress.cefr_level == level,
                LanguageReadingV2StageProgress.internal_stage == internal_stage,
            )
        )
    ).scalar_one_or_none()
    if progress:
        return progress
    progress = LanguageReadingV2StageProgress(
        student_id=student_id,
        language_id=language_id,
        cefr_level=level,
        internal_stage=internal_stage,
        status="locked",
        attempts_completed=0,
        mastery_score=0.0,
        subskill_mastery_json={},
        question_type_mastery_json={},
        recent_attempt_ids_json=[],
    )
    db.add(progress)
    await db.flush()
    return progress


async def build_readiness_gate(
    db: AsyncSession,
    *,
    state_row: LanguageReadingV2StudentState,
    current_stage_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    target = _enum_value(state_row.readiness_target_level)
    if state_row.status == "mastered":
        return {"available": False, "target_level": None, "blocked_reason": "reading_v2_mastered"}
    if not target:
        return {"available": False, "target_level": None, "blocked_reason": "advanced_stage_not_mastered"}
    if state_row.current_stage != "Advanced":
        return {"available": False, "target_level": target, "blocked_reason": "current_stage_is_not_advanced"}
    retake = await readiness_retake_status(db, state_row=state_row)
    if retake["blocked"]:
        return {
            "available": False,
            "target_level": target,
            "blocked_reason": "readiness_retake_requires_more_practice",
            "retake": retake,
        }
    return {
        "available": True,
        "target_level": target,
        "blocked_reason": None,
        "current_stage_evidence": current_stage_evidence,
        "retake": retake,
    }


async def readiness_retake_status(db: AsyncSession, *, state_row: LanguageReadingV2StudentState) -> dict[str, Any]:
    mastery = state_row.recent_mastery_json or {}
    block = ((mastery.get("readiness") or {}).get("retake_block") or {})
    failed_attempt_id = block.get("failed_attempt_id")
    if not failed_attempt_id:
        return {"blocked": False, "required_additional_practice": 0, "completed_additional_practice": 0}
    attempts = await submitted_practice_attempts_for_stage(
        db,
        student_id=state_row.student_id,
        language_id=state_row.language_id,
        cefr_level=_enum_value(state_row.current_cefr) or "A1",
        internal_stage="Advanced",
    )
    completed = len([row for row in attempts if row.id > int(failed_attempt_id)])
    remaining = max(0, READINESS_RETAKE_PRACTICE_ATTEMPTS - completed)
    return {
        "blocked": remaining > 0,
        "failed_attempt_id": failed_attempt_id,
        "required_additional_practice": READINESS_RETAKE_PRACTICE_ATTEMPTS,
        "completed_additional_practice": completed,
        "remaining_additional_practice": remaining,
    }


async def record_readiness_evidence(
    db: AsyncSession, *, attempt: LanguageReadingV2Attempt, question_results: list[ReadingV2QuestionResultOut]
) -> dict[str, Any]:
    state_row = await get_or_create_student_state(db, student_id=attempt.student_id, language_id=attempt.language_id)
    readiness = evaluate_readiness_attempt(attempt, question_results)
    if readiness["passed"]:
        _apply_readiness_pass(state_row, attempt)
        state_row.recent_mastery_json = _merge_recent_mastery(
            state_row.recent_mastery_json,
            {"readiness": {"last_result": readiness, "retake_block": None}},
        )
        return {"passed": True, "next_action": "next_level_unlocked" if _enum_value(attempt.target_next_cefr) else "mastered", "readiness": readiness}

    state_row.recent_mastery_json = _merge_recent_mastery(
        state_row.recent_mastery_json,
        {
            "readiness": {
                "last_result": readiness,
                "retake_block": {
                    "failed_attempt_id": attempt.id,
                    "target_level": _enum_value(attempt.target_next_cefr),
                    "required_additional_practice": READINESS_RETAKE_PRACTICE_ATTEMPTS,
                },
            }
        },
    )
    return {"passed": False, "next_action": "continue_practice", "readiness": readiness}


def evaluate_readiness_attempt(
    attempt: LanguageReadingV2Attempt, question_results: list[ReadingV2QuestionResultOut]
) -> dict[str, Any]:
    subskills = _aggregate_results(question_results, "subskill")
    question_types = _aggregate_results(question_results, "question_type")
    represented_types = set(question_types)
    target_types = set(QUESTION_TYPES)
    core_subskills = _SUBSKILLS_BY_STAGE.get(attempt.internal_stage, [])
    core_evidence = _classify_core_subskills(subskills, core_subskills)
    core_scores = core_evidence["scores"]
    under_sampled_subskills = core_evidence["under_sampled"]
    weak_subskills = core_evidence["weak"]
    total_questions = len(question_results)
    evidence_units = max(1, total_questions // 6)
    requirements = {
        "overall_score_at_least_80": float(attempt.score_percent or 0.0) >= READINESS_PASS_THRESHOLD,
        "mvp_equivalent_evidence": evidence_units >= 2,
        "min_12_answered_questions": total_questions >= READINESS_MIN_ANSWERED_QUESTIONS,
        "all_mvp_question_types_represented": target_types.issubset(represented_types),
        "each_tested_core_subskill_has_min_evidence": not under_sampled_subskills,
        "each_tested_core_subskill_at_least_70": not weak_subskills,
        "no_question_type_below_60": bool(question_types)
        and all(float(value.get("score_percent") or 0.0) >= READINESS_MIN_QUESTION_TYPE_SCORE for value in question_types.values()),
    }
    blocking_reasons = [name for name, passed in requirements.items() if not passed]
    return {
        "passed": not blocking_reasons,
        "requirements": requirements,
        "blocking_reasons": blocking_reasons,
        "score_percent": float(attempt.score_percent or 0.0),
        "total_answered_questions": total_questions,
        "mvp_equivalent_evidence_units": evidence_units,
        "question_types": question_types,
        "subskills": subskills,
        "core_subskill_min_questions": STAGE_MIN_CORE_SUBSKILL_QUESTIONS,
        "core_subskill_evidence": core_evidence["records"],
        "under_sampled_subskills": under_sampled_subskills,
        "weak_subskills": weak_subskills,
        "target_next_cefr": _enum_value(attempt.target_next_cefr),
    }


def _merge_recent_mastery(existing: dict[str, Any] | None, updates: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing or {})
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            nested = dict(merged[key])
            nested.update(value)
            merged[key] = nested
        else:
            merged[key] = value
    return merged


def _aggregate_results(results: list[ReadingV2QuestionResultOut], key: str) -> dict[str, dict[str, float]]:
    buckets: dict[str, list[bool]] = defaultdict(list)
    for result in results:
        buckets[getattr(result, key)].append(result.correct)
    return {
        name: {
            "correct": float(sum(1 for value in values if value)),
            "total": float(len(values)),
            "score_percent": round((sum(1 for value in values if value) / len(values)) * 100.0, 2),
        }
        for name, values in buckets.items()
    }


def _has_major_weakness(subskill_mastery: dict[str, Any] | None) -> bool:
    if not subskill_mastery:
        return True
    return any(float(value.get("score_percent") or 0.0) < 60.0 for value in subskill_mastery.values())


def _apply_readiness_pass(state_row: LanguageReadingV2StudentState, attempt: LanguageReadingV2Attempt) -> None:
    target = _enum_value(attempt.target_next_cefr)
    if not target:
        state_row.status = "mastered"
        return
    state_row.current_cefr = LanguageLevel(target)
    state_row.current_stage = "Beginner"
    state_row.unlocked_rank = stage_rank(target, "Beginner")
    state_row.readiness_target_level = None
    state_row.status = "active"


def _next_action(attempt: LanguageReadingV2Attempt, passed: bool) -> str:
    if attempt.mode == "readiness":
        if not passed:
            return "continue_practice"
        return "mastered" if not _enum_value(attempt.target_next_cefr) else "next_level_unlocked"
    return "continue_practice"


async def build_reading_v2_history(
    db: AsyncSession, *, student_id: int, language_id: int, limit: int = 30
) -> ReadingV2HistoryOut:
    limit = min(max(int(limit or 30), 1), 100)
    result = await db.execute(
        select(LanguageReadingV2Attempt)
        .where(
            LanguageReadingV2Attempt.student_id == student_id,
            LanguageReadingV2Attempt.language_id == language_id,
        )
        .order_by(LanguageReadingV2Attempt.created_at.desc())
        .limit(limit)
    )
    attempts = []
    for attempt in result.scalars().all():
        attempts.append(
            {
                "attempt_id": attempt.id,
                "mode": attempt.mode,
                "status": attempt.status,
                "cefr_level": _enum_value(attempt.cefr_level),
                "internal_stage": attempt.internal_stage,
                "score_percent": attempt.score_percent,
                "created_at": attempt.created_at,
                "submitted_at": attempt.submitted_at,
            }
        )
    return ReadingV2HistoryOut(attempts=attempts)


def _stage_path_summary(
    *,
    progress: LanguageReadingV2StageProgress | None,
    rank: int,
    state_row: LanguageReadingV2StudentState,
    current_rank: int,
) -> dict[str, Any]:
    if progress:
        summary = dict(progress.subskill_mastery_json or {})
        summary["question_types"] = progress.question_type_mastery_json or {}
        summary["recent_attempt_ids"] = progress.recent_attempt_ids_json or []
        if rank == current_rank:
            current_evidence = (state_row.recent_mastery_json or {}).get("current_stage_evidence") or {}
            summary["current"] = True
            summary["evidence"] = current_evidence
            blocking = current_evidence.get("blocking_reasons") or []
            summary["locked_reason"] = blocking[0] if blocking else None
        if progress.status == "mastered":
            summary["mastered_at"] = progress.mastered_at
        return summary
    if rank > int(state_row.unlocked_rank or 0):
        return {"locked_reason": "previous_stage_not_mastered"}
    if rank == current_rank:
        return {"locked_reason": None, "current": True}
    return {"locked_reason": None}
