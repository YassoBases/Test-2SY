from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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

CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
INTERNAL_STAGES = ["Beginner", "Intermediate", "Advanced"]
QUESTION_TYPES = ["mcq", "gap_fill", "true_false", "short_answer"]
PROMPT_VERSION = "reading_v2_r1"
VALIDATOR_VERSION = "reading_v2_validator_r1"
MODEL_USED = "local_mock"
MIN_STAGE_EVIDENCE_ATTEMPTS = 6
MASTERY_THRESHOLD = 80.0
PRACTICE_PASS_THRESHOLD = 70.0
READINESS_PASS_THRESHOLD = 80.0

_WORD_RANGES: dict[str, dict[str, tuple[int, int]]] = {
    "A1": {"Beginner": (80, 110), "Intermediate": (100, 140), "Advanced": (125, 170)},
    "A2": {"Beginner": (150, 210), "Intermediate": (190, 260), "Advanced": (240, 320)},
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


def stage_rank(cefr_level: str | LanguageLevel, internal_stage: str) -> int:
    level = cefr_level.value if isinstance(cefr_level, LanguageLevel) else str(cefr_level)
    return CEFR_LEVELS.index(level) * len(INTERNAL_STAGES) + INTERNAL_STAGES.index(internal_stage)


def next_cefr_level(cefr_level: str | LanguageLevel) -> str | None:
    level = cefr_level.value if isinstance(cefr_level, LanguageLevel) else str(cefr_level)
    index = CEFR_LEVELS.index(level)
    return CEFR_LEVELS[index + 1] if index + 1 < len(CEFR_LEVELS) else None


def _enum_value(value: str | LanguageLevel | None) -> str | None:
    return value.value if isinstance(value, LanguageLevel) else value


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
    state_row = LanguageReadingV2StudentState(
        student_id=student_id,
        language_id=language_id,
        current_cefr=initial_level,
        current_stage="Beginner",
        status="active",
        unlocked_rank=stage_rank(initial_level, "Beginner"),
        recent_mastery_json={},
    )
    db.add(state_row)
    await db.flush()
    return state_row


async def build_generation_blueprint(
    db: AsyncSession, *, student_id: int, language_id: int, mode: ReadingV2Mode = "practice"
) -> GenerationBlueprint:
    state_row = await get_or_create_student_state(db, student_id=student_id, language_id=language_id)
    cefr = _enum_value(state_row.current_cefr) or "A1"
    stage = state_row.current_stage
    word_min, word_max = _WORD_RANGES[cefr][stage]
    question_count = 8 if mode == "readiness" else 4
    question_types = (QUESTION_TYPES * ((question_count // len(QUESTION_TYPES)) + 1))[:question_count]
    target_next = next_cefr_level(cefr) if mode == "readiness" else None
    topic = "everyday learning habits" if mode == "practice" else f"{target_next or cefr} readiness"

    return GenerationBlueprint(
        cefr_level=cefr,
        internal_stage=stage,
        mode=mode,
        word_count_min=word_min,
        word_count_max=word_max,
        sentence_complexity=f"{cefr.lower()}_{stage.lower()}_sentences",
        vocabulary_difficulty=f"{cefr.lower()}_{stage.lower()}_vocabulary",
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
            "true_false",
            "scan_detail",
            "Mira checks context before using a dictionary.",
            {"correct": True},
            [],
        ),
        (
            "gap_fill",
            "vocab_in_context",
            "The group writes simple notes in the ____.",
            {"accepted_answers": ["margin"]},
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
    for i, question_type in enumerate(blueprint.question_types, start=1):
        spec = answer_specs[(i - 1) % len(answer_specs)]
        q_type, subskill, stem, answer_key, choices = spec
        if question_type != q_type:
            q_type = question_type
            stem = f"Answer this {question_type.replace('_', ' ')} question about Mira's reading routine."
            answer_key = _fallback_answer_key(question_type)
            choices = _fallback_choices(question_type)
            subskill = blueprint.reading_subskills[(i - 1) % len(blueprint.reading_subskills)]
        questions.append(
            {
                "id": f"q{i}",
                "type": q_type,
                "subskill": subskill,
                "stem": stem,
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
        questions=questions,
        safety_tags=["education", "low_risk"],
    )


def _fallback_answer_key(question_type: str) -> dict[str, Any]:
    if question_type == "mcq":
        return {"correct_choice_id": "a"}
    if question_type == "true_false":
        return {"correct": True}
    if question_type == "gap_fill":
        return {"accepted_answers": ["title"]}
    return {"accepted_answers": ["title"], "required_key_terms": ["title"]}


def _fallback_choices(question_type: str) -> list[dict[str, str]]:
    if question_type != "mcq":
        return []
    return [
        {"id": "a", "text": "A helpful reading strategy."},
        {"id": "b", "text": "A cooking instruction."},
        {"id": "c", "text": "A weather report."},
    ]


def validate_generated_activity(activity: dict[str, Any] | GeneratedReadingActivity, blueprint: GenerationBlueprint) -> ValidationResult:
    issues: list[ValidationIssue] = []
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
        if _leaks_answer(question.stem, answer_key, question.choices, q_type):
            issues.append(ValidationIssue(code="answer_leakage", message="Question stem leaks the answer", question_id=question.id))
        if q_type == "mcq":
            _validate_mcq(question, answer_key, issues)
        elif q_type == "gap_fill":
            if not answer_key.get("accepted_answers"):
                issues.append(ValidationIssue(code="missing_gap_fill_answers", message="Gap Fill needs accepted answers", question_id=question.id))
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

    return ValidationResult(valid=not issues, issues=issues)


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
            )
        )
    score_percent = round((correct_count / len(parsed.questions)) * 100.0, 2) if parsed.questions else 0.0
    return score_percent, results


def _score_question(question_type: str, answer_key: dict[str, Any], answer: Any) -> bool:
    if isinstance(answer, dict):
        candidate = answer.get("choice_id")
        if candidate is None:
            candidate = answer.get("value")
        if candidate is None:
            candidate = answer.get("answer")
    else:
        candidate = answer
    if question_type == "mcq":
        return str(candidate or "") == str(answer_key.get("correct_choice_id") or "")
    if question_type == "true_false":
        return _as_bool(candidate) is answer_key.get("correct")
    if question_type == "gap_fill":
        normalized = _normalize_text(str(candidate or ""))
        return normalized in {_normalize_text(str(item)) for item in answer_key.get("accepted_answers") or []}
    if question_type == "short_answer":
        normalized = _normalize_text(str(candidate or ""))
        accepted = {_normalize_text(str(item)) for item in answer_key.get("accepted_answers") or []}
        if normalized in accepted:
            return True
        required = [_normalize_text(str(item)) for item in answer_key.get("required_key_terms") or []]
        return bool(required) and all(term in normalized for term in required)
    return False


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
    blueprint = await build_generation_blueprint(db, student_id=student_id, language_id=language_id, mode=mode)
    activity = generate_reading_activity_from_blueprint(blueprint)
    validation = validate_generated_activity(activity, blueprint)
    target_next = next_cefr_level(blueprint.cefr_level) if mode == "readiness" else None
    attempt = LanguageReadingV2Attempt(
        student_id=student_id,
        language_id=language_id,
        cefr_level=LanguageLevel(blueprint.cefr_level),
        internal_stage=blueprint.internal_stage,
        mode=mode,
        status="ready" if validation.valid else "generation_failed",
        target_next_cefr=LanguageLevel(target_next) if target_next else None,
        generation_blueprint_json=blueprint.model_dump(),
        generated_activity_json=activity.model_dump(),
        validation_result_json=validation.model_dump(),
        model_used=MODEL_USED,
        prompt_version=blueprint.prompt_version,
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
    return ReadingV2OverviewOut(
        student_id=student_id,
        language_id=language_id,
        current_cefr=_enum_value(state_row.current_cefr) or "A1",
        current_stage=state_row.current_stage,
        status=state_row.status,
        readiness_target_level=_enum_value(state_row.readiness_target_level),
        recent_mastery=state_row.recent_mastery_json or {},
        next_action="readiness" if state_row.readiness_target_level else "practice",
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
                    recent_mastery=(progress.subskill_mastery_json or {}) if progress else {},
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

    await record_attempt_evidence(db, attempt=attempt, question_results=question_results)
    state_row = await get_or_create_student_state(db, student_id=student_id, language_id=language_id)
    passed = score_percent >= (READINESS_PASS_THRESHOLD if attempt.mode == "readiness" else PRACTICE_PASS_THRESHOLD)
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
        next_action=_next_action(attempt, passed),
    )


async def record_attempt_evidence(
    db: AsyncSession, *, attempt: LanguageReadingV2Attempt, question_results: list[ReadingV2QuestionResultOut]
) -> None:
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
    old_mastery = float(progress.mastery_score or 0.0)
    new_score = float(attempt.score_percent or 0.0)
    progress.mastery_score = round(((old_mastery * old_attempts) + new_score) / progress.attempts_completed, 2)
    progress.subskill_mastery_json = _aggregate_results(question_results, "subskill")
    progress.question_type_mastery_json = _aggregate_results(question_results, "question_type")
    recent_ids = list(progress.recent_attempt_ids_json or [])
    recent_ids.append(attempt.id)
    progress.recent_attempt_ids_json = recent_ids[-10:]

    state_row = await get_or_create_student_state(db, student_id=attempt.student_id, language_id=attempt.language_id)
    state_row.recent_mastery_json = {
        "attempts_completed": progress.attempts_completed,
        "mastery_score": progress.mastery_score,
        "subskills": progress.subskill_mastery_json,
        "question_types": progress.question_type_mastery_json,
        "evidence_sufficient": progress.attempts_completed >= MIN_STAGE_EVIDENCE_ATTEMPTS,
    }
    if progress.attempts_completed < MIN_STAGE_EVIDENCE_ATTEMPTS:
        return
    if progress.mastery_score < MASTERY_THRESHOLD:
        return
    if _has_major_weakness(progress.subskill_mastery_json):
        return
    if attempt.mode == "readiness" and attempt.score_percent and attempt.score_percent >= READINESS_PASS_THRESHOLD:
        _apply_readiness_pass(state_row, attempt)


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
