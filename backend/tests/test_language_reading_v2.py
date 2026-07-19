from __future__ import annotations

import asyncio
import json
import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy import select

import app.services.language_reading_v2_service as reading_service
from app.models.language.analytics import LanguageAnalytics
from app.models.language.catalog import Language
from app.models.language.enums import LanguageLevel
from app.models.language.reading_v2 import (
    LanguageReadingV2Attempt,
    LanguageReadingV2StageProgress,
    LanguageReadingV2StudentState,
)
from app.models.user import User, UserRole
from app.schemas.language_reading_v2 import GenerationBlueprint
from app.services.language_reading_v2_service import (
    CEFR_LEVELS,
    INTERNAL_STAGES,
    build_generation_blueprint,
    build_reading_v2_overview,
    build_reading_v2_path,
    create_reading_v2_attempt,
    generate_activity_with_ai_provider,
    generate_reading_activity_from_blueprint,
    reading_v2_generation_prompt,
    score_generated_activity,
    select_reading_v2_generation_provider,
    submit_reading_v2_attempt,
    validate_generated_activity,
)

pytestmark = pytest.mark.postgresql


async def _student_and_language(db, *, reading_level: LanguageLevel | None = None) -> tuple[int, int]:
    marker = uuid.uuid4().hex[:10]
    student = User(
        email=f"reading-v2-{marker}@example.com",
        name="Reading V2 Student",
        hashed_password="test",
        role=UserRole.student,
    )
    language = Language(
        code=f"rv{marker[:8]}",
        name_en="Reading V2 English",
        name_ar="Reading V2 English",
        is_active=True,
    )
    db.add_all([student, language])
    await db.flush()
    if reading_level:
        db.add(
            LanguageAnalytics(
                student_id=student.id,
                language_id=language.id,
                reading_level=reading_level,
            )
        )
        await db.flush()
    return student.id, language.id


def _blueprint(**overrides) -> GenerationBlueprint:
    values = {
        "cefr_level": "A2",
        "internal_stage": "Intermediate",
        "mode": "practice",
        "word_count_min": 90,
        "word_count_max": 140,
        "sentence_complexity": "a2_intermediate_sentences",
        "vocabulary_difficulty": "a2_intermediate_vocabulary",
        "target_vocab_tags": ["travel"],
        "required_vocab_items": [],
        "target_grammar_tags": ["past_simple"],
        "banned_above_level_grammar": ["conditionals"],
        "reading_subskills": ["skim_gist", "scan_detail", "vocab_in_context", "literal_comprehension"],
        "question_types": ["mcq", "true_false", "gap_fill", "short_answer"],
        "topic": "safe study habits",
        "difficulty_score": 35.0,
        "inference_depth": "mixed",
        "number_of_questions": 4,
        "safety_topic_restrictions": ["unsafe topics"],
        "prompt_version": "reading_v2_r5_gap_fill",
    }
    values.update(overrides)
    return GenerationBlueprint(**values)


def _install_unique_mock_generator(monkeypatch):
    counter = {"value": 0}

    async def fake_generate_activity_for_blueprint(blueprint):
        counter["value"] += 1
        activity = generate_reading_activity_from_blueprint(blueprint).model_dump()
        activity["title"] = f"{activity['title']} #{counter['value']}"
        activity["validation_metadata"]["test_unique_marker"] = counter["value"]
        validation = validate_generated_activity(activity, blueprint)
        return reading_service.ReadingV2GenerationOutcome(
            activity=activity,
            validation=validation,
            provider_name="local_mock",
            model_used="local_mock",
            prompt_version=blueprint.prompt_version,
            retry_count=0,
        )

    monkeypatch.setattr(reading_service, "generate_activity_for_blueprint", fake_generate_activity_for_blueprint)


async def _move_to_stage(
    db,
    *,
    student_id: int,
    language_id: int,
    cefr: LanguageLevel = LanguageLevel.A1,
    stage: str = "Beginner",
    readiness_target: LanguageLevel | None = None,
    stage_status: str = "current",
) -> None:
    state = await reading_service.get_or_create_student_state(db, student_id=student_id, language_id=language_id)
    state.current_cefr = cefr
    state.current_stage = stage
    state.status = "active"
    state.unlocked_rank = reading_service.stage_rank(cefr, stage)
    state.readiness_target_level = readiness_target
    progress = await reading_service.get_or_create_stage_progress(
        db,
        student_id=student_id,
        language_id=language_id,
        cefr_level=cefr,
        internal_stage=stage,
    )
    progress.status = stage_status
    await db.flush()


def _answers_for_activity(activity: dict, *, wrong_subskills: set[str] | None = None, wrong_count: int = 0) -> dict:
    wrong_subskills = wrong_subskills or set()
    answers = {}
    wrong_remaining = wrong_count
    for question in activity["questions"]:
        key = question.get("answer_key") or {}
        should_miss = question["subskill"] in wrong_subskills or wrong_remaining > 0
        if should_miss and wrong_remaining > 0:
            wrong_remaining -= 1
        if should_miss:
            answers[question["id"]] = {"choice_id": "__wrong__"} if question["type"] == "mcq" else "__wrong__"
            continue
        if question["type"] == "mcq":
            answers[question["id"]] = {"choice_id": key.get("correct_choice_id")}
        elif question["type"] == "true_false":
            answers[question["id"]] = key.get("correct")
        elif question["type"] in {"gap_fill", "short_answer"}:
            answers[question["id"]] = (key.get("accepted_answers") or key.get("required_key_terms") or [""])[0]
    return answers


async def _create_and_submit_practice(
    db,
    *,
    student_id: int,
    language_id: int,
    wrong_subskills: set[str] | None = None,
    wrong_count: int = 0,
):
    attempt = await create_reading_v2_attempt(db, student_id=student_id, language_id=language_id, mode="practice")
    stored = (
        await db.execute(select(LanguageReadingV2Attempt).where(LanguageReadingV2Attempt.id == attempt.attempt_id))
    ).scalar_one()
    return await submit_reading_v2_attempt(
        db,
        student_id=student_id,
        language_id=language_id,
        attempt_id=attempt.attempt_id,
        answers=_answers_for_activity(
            stored.generated_activity_json,
            wrong_subskills=wrong_subskills,
            wrong_count=wrong_count,
        ),
    )


async def _create_and_submit_readiness(
    db,
    *,
    student_id: int,
    language_id: int,
    wrong_count: int = 0,
):
    attempt = await create_reading_v2_attempt(db, student_id=student_id, language_id=language_id, mode="readiness")
    stored = (
        await db.execute(select(LanguageReadingV2Attempt).where(LanguageReadingV2Attempt.id == attempt.attempt_id))
    ).scalar_one()
    return await submit_reading_v2_attempt(
        db,
        student_id=student_id,
        language_id=language_id,
        attempt_id=attempt.attempt_id,
        answers=_answers_for_activity(stored.generated_activity_json, wrong_count=wrong_count),
    )


def test_generated_activity_validation_passes_for_valid_mock_activity():
    blueprint = _blueprint()
    activity = generate_reading_activity_from_blueprint(blueprint)

    result = validate_generated_activity(activity, blueprint)

    assert result.valid is True
    assert result.issues == []


def test_validation_rejects_malformed_activity():
    result = validate_generated_activity({"passage": ""}, _blueprint())

    assert result.valid is False
    assert any(issue.code == "invalid_shape" for issue in result.issues)


def test_validation_rejects_unsupported_question_type():
    blueprint = _blueprint()
    activity = generate_reading_activity_from_blueprint(blueprint).model_dump()
    activity["questions"][0]["type"] = "matching_headings"

    result = validate_generated_activity(activity, blueprint)

    assert result.valid is False
    assert any(issue.code == "unsupported_question_type" for issue in result.issues)


def test_validation_rejects_missing_answer_keys():
    blueprint = _blueprint()
    activity = generate_reading_activity_from_blueprint(blueprint).model_dump()
    activity["questions"][0]["answer_key"] = None

    result = validate_generated_activity(activity, blueprint)

    assert result.valid is False
    assert any(issue.code == "missing_answer_key" for issue in result.issues)


def test_validation_rejects_answer_leakage():
    blueprint = _blueprint()
    activity = generate_reading_activity_from_blueprint(blueprint).model_dump()
    activity["questions"][0]["stem"] = "Mira learns helpful ways to read more confidently."

    result = validate_generated_activity(activity, blueprint)

    assert result.valid is False
    assert any(issue.code == "answer_leakage" for issue in result.issues)


def test_validation_rejects_gap_fill_without_visible_blank_sentence():
    blueprint = _blueprint(question_types=["gap_fill"], number_of_questions=1)
    activity = generate_reading_activity_from_blueprint(blueprint).model_dump()
    question = activity["questions"][0]
    question["stem"] = "Complete the missing word from the passage."
    question["sentence_with_blank"] = None

    result = validate_generated_activity(activity, blueprint)

    assert result.valid is False
    assert any(issue.code == "missing_gap_fill_sentence" for issue in result.issues)


def test_validation_rejects_gap_fill_with_multiple_blanks():
    blueprint = _blueprint(question_types=["gap_fill"], number_of_questions=1)
    activity = generate_reading_activity_from_blueprint(blueprint).model_dump()
    activity["questions"][0]["sentence_with_blank"] = "Mira checks ____ and writes ____."

    result = validate_generated_activity(activity, blueprint)

    assert result.valid is False
    assert any(issue.code == "invalid_gap_fill_blank" for issue in result.issues)


def test_deterministic_scoring_works_for_mvp_question_types():
    blueprint = _blueprint()
    activity = generate_reading_activity_from_blueprint(blueprint)

    score, results = score_generated_activity(
        activity,
        {
            "q1": {"choice_id": "a"},
            "q2": True,
            "q3": "Margin!",
            "q4": "She checks the title first.",
        },
    )

    assert score == 100.0
    assert [result.question_type for result in results] == ["mcq", "true_false", "gap_fill", "short_answer"]
    assert all(result.correct for result in results)


def test_provider_selection_defaults_to_safe_local_mock(monkeypatch):
    monkeypatch.setattr(reading_service.settings, "READING_V2_GENERATION_PROVIDER", "local_mock")

    assert select_reading_v2_generation_provider() == "local_mock"

    monkeypatch.setattr(reading_service.settings, "READING_V2_GENERATION_PROVIDER", "ai")
    assert select_reading_v2_generation_provider() == "ai"

    monkeypatch.setattr(reading_service.settings, "READING_V2_GENERATION_PROVIDER", "unknown")
    assert select_reading_v2_generation_provider() == "local_mock"


def test_ai_prompt_contains_required_blueprint_controls():
    prompt = reading_v2_generation_prompt(_blueprint())
    prompt_text = f"{prompt['system']}\n{prompt['user']}"

    for required in [
        "cefr_level",
        "internal_stage",
        "word_count_min",
        "word_count_max",
        "sentence_complexity",
        "vocabulary_difficulty",
        "target_vocab_tags",
        "required_vocab_items",
        "target_grammar_tags",
        "banned_above_level_grammar",
        "reading_subskills",
        "question_types",
        "student_interest",
        "difficulty_score",
        "inference_depth",
        "number_of_questions",
        "safety_topic_restrictions",
        "sentence_with_blank",
        "exactly one visible ____ marker",
        "For A1 Beginner",
        "avoid abstract wording",
        "Return valid JSON only",
    ]:
        assert required in prompt_text


async def test_valid_ai_json_becomes_usable_generation(monkeypatch):
    blueprint = _blueprint()
    activity = generate_reading_activity_from_blueprint(blueprint).model_dump()

    async def fake_generate_llm_json(*_args, **_kwargs):
        return json.dumps(activity)

    monkeypatch.setattr(reading_service, "generate_llm_json", fake_generate_llm_json)

    outcome = await generate_activity_with_ai_provider(blueprint)

    assert outcome.validation.valid is True
    assert outcome.provider_name == "ai"
    assert outcome.model_used == reading_service.reading_v2_ai_model_name()
    assert outcome.retry_count == 0
    assert outcome.activity
    assert outcome.activity["validation_metadata"]["provider"] == "ai"


async def test_invalid_ai_json_triggers_retry_then_valid_generation(monkeypatch):
    blueprint = _blueprint()
    valid_activity = generate_reading_activity_from_blueprint(blueprint).model_dump()
    calls = []

    async def fake_generate_llm_json(prompt, **kwargs):
        calls.append({"prompt": prompt, "kwargs": kwargs})
        if len(calls) == 1:
            invalid = dict(valid_activity)
            invalid["cefr_level"] = "B1"
            return json.dumps(invalid)
        return json.dumps(valid_activity)

    monkeypatch.setattr(reading_service.settings, "READING_V2_AI_MAX_RETRIES", 2)
    monkeypatch.setattr(reading_service, "generate_llm_json", fake_generate_llm_json)

    outcome = await generate_activity_with_ai_provider(blueprint)

    assert outcome.validation.valid is True
    assert outcome.retry_count == 1
    assert len(calls) == 2
    assert "Validation errors from the previous generated JSON" in calls[1]["prompt"]


async def test_invalid_ai_json_after_max_retries_fails_gracefully(monkeypatch):
    blueprint = _blueprint()

    async def fake_generate_llm_json(*_args, **_kwargs):
        return "not json"

    monkeypatch.setattr(reading_service.settings, "READING_V2_AI_MAX_RETRIES", 1)
    monkeypatch.setattr(reading_service, "generate_llm_json", fake_generate_llm_json)

    outcome = await generate_activity_with_ai_provider(blueprint)

    assert outcome.validation.valid is False
    assert outcome.retry_count == 1
    assert outcome.activity is None
    assert any(issue.code == "invalid_json" for issue in outcome.validation.issues)


async def test_initial_overview_creates_safe_state(postgres_session):
    student_id, language_id = await _student_and_language(postgres_session)

    overview = await build_reading_v2_overview(postgres_session, student_id=student_id, language_id=language_id)

    assert overview.current_cefr == "A1"
    assert overview.current_stage == "Beginner"
    assert overview.next_action == "practice"
    stored = (
        await postgres_session.execute(
            select(LanguageReadingV2StudentState).where(
                LanguageReadingV2StudentState.student_id == student_id,
                LanguageReadingV2StudentState.language_id == language_id,
            )
        )
    ).scalar_one()
    assert stored.status == "active"


async def test_path_returns_all_cefr_levels_and_stages(postgres_session):
    student_id, language_id = await _student_and_language(postgres_session)

    path = await build_reading_v2_path(postgres_session, student_id=student_id, language_id=language_id)

    assert len(path.stages) == len(CEFR_LEVELS) * len(INTERNAL_STAGES)
    assert {(stage.cefr_level, stage.internal_stage) for stage in path.stages} == {
        (level, internal_stage) for level in CEFR_LEVELS for internal_stage in INTERNAL_STAGES
    }


async def test_parallel_overview_and_path_create_initial_state_once(postgres_session_factory):
    async with postgres_session_factory() as setup:
        student_id, language_id = await _student_and_language(setup)
        await setup.commit()

    async def load_overview():
        async with postgres_session_factory() as db:
            result = await build_reading_v2_overview(db, student_id=student_id, language_id=language_id)
            await db.commit()
            return result

    async def load_path():
        async with postgres_session_factory() as db:
            result = await build_reading_v2_path(db, student_id=student_id, language_id=language_id)
            await db.commit()
            return result

    overview, path = await asyncio.gather(load_overview(), load_path())

    assert overview.current_cefr == "A1"
    assert len(path.stages) == len(CEFR_LEVELS) * len(INTERNAL_STAGES)
    async with postgres_session_factory() as db:
        rows = (
            await db.execute(
                select(LanguageReadingV2StudentState).where(
                    LanguageReadingV2StudentState.student_id == student_id,
                    LanguageReadingV2StudentState.language_id == language_id,
                )
            )
        ).scalars().all()
    assert len(rows) == 1


async def test_generation_blueprint_matches_student_level_and_stage(postgres_session):
    student_id, language_id = await _student_and_language(postgres_session, reading_level=LanguageLevel.B1)

    blueprint = await build_generation_blueprint(
        postgres_session,
        student_id=student_id,
        language_id=language_id,
    )

    assert blueprint.cefr_level == "B1"
    assert blueprint.internal_stage == "Beginner"
    assert blueprint.word_count_min < blueprint.word_count_max
    assert set(["mcq", "gap_fill", "true_false", "short_answer"]).issubset(set(blueprint.question_types))


async def test_a1_beginner_blueprint_uses_short_simple_constraints(postgres_session):
    student_id, language_id = await _student_and_language(postgres_session, reading_level=LanguageLevel.A1)

    blueprint = await build_generation_blueprint(
        postgres_session,
        student_id=student_id,
        language_id=language_id,
    )

    assert blueprint.cefr_level == "A1"
    assert blueprint.internal_stage == "Beginner"
    assert blueprint.word_count_min == 55
    assert blueprint.word_count_max == 80
    assert "simple_present" in blueprint.sentence_complexity
    assert "concrete" in blueprint.vocabulary_difficulty


async def test_attempt_creation_stores_snapshots_and_strips_student_keys(postgres_session):
    student_id, language_id = await _student_and_language(postgres_session, reading_level=LanguageLevel.A2)

    out = await create_reading_v2_attempt(postgres_session, student_id=student_id, language_id=language_id)

    stored = (
        await postgres_session.execute(
            select(LanguageReadingV2Attempt).where(LanguageReadingV2Attempt.id == out.attempt_id)
        )
    ).scalar_one()
    assert stored.generation_blueprint_json["cefr_level"] == "A2"
    assert stored.generation_blueprint_json["generation_provider"] == "local_mock"
    assert stored.generation_blueprint_json["generation_retry_count"] == 0
    assert stored.generated_activity_json["questions"]
    assert stored.validation_result_json["valid"] is True
    assert stored.validation_result_json["generation_provider"] == "local_mock"
    assert stored.model_used == "local_mock"
    assert all("answer_key" not in question for question in out.activity["questions"])
    assert "accepted_answers" not in str(out.activity)
    assert "required_key_terms" not in str(out.activity)


async def test_attempt_creation_uses_configured_ai_provider_with_mocked_ai(monkeypatch, postgres_session):
    student_id, language_id = await _student_and_language(postgres_session, reading_level=LanguageLevel.A2)
    blueprint = await build_generation_blueprint(postgres_session, student_id=student_id, language_id=language_id)
    activity = generate_reading_activity_from_blueprint(blueprint).model_dump()

    async def fake_generate_llm_json(*_args, **_kwargs):
        return json.dumps(activity)

    monkeypatch.setattr(reading_service.settings, "READING_V2_GENERATION_PROVIDER", "ai")
    monkeypatch.setattr(reading_service.settings, "READING_V2_AI_MAX_RETRIES", 1)
    monkeypatch.setattr(reading_service.settings, "READING_V2_AI_MODEL", "test-ai-model")
    monkeypatch.setattr(reading_service, "generate_llm_json", fake_generate_llm_json)

    out = await create_reading_v2_attempt(postgres_session, student_id=student_id, language_id=language_id)

    stored = (
        await postgres_session.execute(
            select(LanguageReadingV2Attempt).where(LanguageReadingV2Attempt.id == out.attempt_id)
        )
    ).scalar_one()
    assert stored.status == "ready"
    assert stored.model_used == "test-ai-model"
    assert stored.generation_blueprint_json["generation_provider"] == "ai"
    assert stored.validation_result_json["generation_provider"] == "ai"
    assert all("answer_key" not in question for question in out.activity["questions"])


async def test_failed_generation_does_not_create_usable_attempt(monkeypatch, postgres_session):
    student_id, language_id = await _student_and_language(postgres_session, reading_level=LanguageLevel.A2)

    async def fake_generate_llm_json(*_args, **_kwargs):
        return "not json"

    monkeypatch.setattr(reading_service.settings, "READING_V2_GENERATION_PROVIDER", "ai")
    monkeypatch.setattr(reading_service.settings, "READING_V2_AI_MAX_RETRIES", 0)
    monkeypatch.setattr(reading_service, "generate_llm_json", fake_generate_llm_json)

    with pytest.raises(HTTPException):
        await create_reading_v2_attempt(postgres_session, student_id=student_id, language_id=language_id)

    rows = (
        await postgres_session.execute(
            select(LanguageReadingV2Attempt).where(
                LanguageReadingV2Attempt.student_id == student_id,
                LanguageReadingV2Attempt.language_id == language_id,
            )
        )
    ).scalars().all()
    assert rows
    assert all(row.status == "generation_failed" for row in rows)
    assert all(row.submitted_at is None for row in rows)


async def test_xp_alone_does_not_progress_stage(postgres_session):
    student_id, language_id = await _student_and_language(postgres_session)

    await build_reading_v2_overview(postgres_session, student_id=student_id, language_id=language_id)
    postgres_session.add(
        LanguageReadingV2StageProgress(
            student_id=student_id,
            language_id=language_id,
            cefr_level=LanguageLevel.A1,
            internal_stage="Beginner",
            status="current",
            attempts_completed=99,
            mastery_score=100.0,
            subskill_mastery_json={},
            question_type_mastery_json={},
            recent_attempt_ids_json=[],
        )
    )
    await postgres_session.flush()

    path = await build_reading_v2_path(postgres_session, student_id=student_id, language_id=language_id)
    overview = await build_reading_v2_overview(postgres_session, student_id=student_id, language_id=language_id)

    current = [stage for stage in path.stages if stage.status == "current"]
    assert [(stage.cefr_level, stage.internal_stage) for stage in current] == [("A1", "Beginner")]
    assert overview.current_stage == "Beginner"
    assert "min_5_submitted_practice_attempts" in overview.recent_mastery["current_stage_evidence"]["blocking_reasons"]


async def test_fewer_than_5_attempts_cannot_progress(monkeypatch, postgres_session):
    _install_unique_mock_generator(monkeypatch)
    student_id, language_id = await _student_and_language(postgres_session)

    for _ in range(4):
        await _create_and_submit_practice(postgres_session, student_id=student_id, language_id=language_id)

    overview = await build_reading_v2_overview(postgres_session, student_id=student_id, language_id=language_id)

    assert overview.current_cefr == "A1"
    assert overview.current_stage == "Beginner"
    assert overview.recent_mastery["evidence_sufficient"] is False
    assert "min_5_submitted_practice_attempts" in overview.recent_mastery["current_stage_evidence"]["blocking_reasons"]


async def test_low_recent_score_blocks_progression(monkeypatch, postgres_session):
    _install_unique_mock_generator(monkeypatch)
    student_id, language_id = await _student_and_language(postgres_session)

    for _ in range(4):
        await _create_and_submit_practice(postgres_session, student_id=student_id, language_id=language_id)
    await _create_and_submit_practice(postgres_session, student_id=student_id, language_id=language_id, wrong_count=2)

    overview = await build_reading_v2_overview(postgres_session, student_id=student_id, language_id=language_id)

    assert overview.current_stage == "Beginner"
    reasons = overview.recent_mastery["current_stage_evidence"]["blocking_reasons"]
    assert "no_recent_attempt_below_70" in reasons


async def test_one_weak_subskill_blocks_progression(monkeypatch, postgres_session):
    _install_unique_mock_generator(monkeypatch)
    student_id, language_id = await _student_and_language(postgres_session)

    await _create_and_submit_practice(
        postgres_session, student_id=student_id, language_id=language_id, wrong_subskills={"skim_gist"}
    )
    await _create_and_submit_practice(
        postgres_session, student_id=student_id, language_id=language_id, wrong_subskills={"skim_gist"}
    )
    for _ in range(3):
        await _create_and_submit_practice(postgres_session, student_id=student_id, language_id=language_id)

    overview = await build_reading_v2_overview(postgres_session, student_id=student_id, language_id=language_id)

    assert overview.current_stage == "Beginner"
    evidence = overview.recent_mastery["current_stage_evidence"]
    assert evidence["core_subskill_scores"]["skim_gist"] < 70.0
    assert "each_core_subskill_at_least_70" in evidence["blocking_reasons"]


async def test_enough_evidence_unlocks_next_internal_stage(monkeypatch, postgres_session):
    _install_unique_mock_generator(monkeypatch)
    student_id, language_id = await _student_and_language(postgres_session)

    for _ in range(5):
        await _create_and_submit_practice(postgres_session, student_id=student_id, language_id=language_id)

    overview = await build_reading_v2_overview(postgres_session, student_id=student_id, language_id=language_id)
    path = await build_reading_v2_path(postgres_session, student_id=student_id, language_id=language_id)

    assert overview.current_cefr == "A1"
    assert overview.current_stage == "Intermediate"
    by_stage = {(stage.cefr_level, stage.internal_stage): stage for stage in path.stages}
    assert by_stage[("A1", "Beginner")].status == "mastered"
    assert by_stage[("A1", "Intermediate")].status == "current"


async def test_advanced_mastery_unlocks_readiness(monkeypatch, postgres_session):
    _install_unique_mock_generator(monkeypatch)
    student_id, language_id = await _student_and_language(postgres_session)
    await _move_to_stage(
        postgres_session,
        student_id=student_id,
        language_id=language_id,
        cefr=LanguageLevel.A1,
        stage="Advanced",
    )

    for _ in range(5):
        await _create_and_submit_practice(postgres_session, student_id=student_id, language_id=language_id)

    overview = await build_reading_v2_overview(postgres_session, student_id=student_id, language_id=language_id)
    path = await build_reading_v2_path(postgres_session, student_id=student_id, language_id=language_id)
    advanced = [stage for stage in path.stages if stage.cefr_level == "A1" and stage.internal_stage == "Advanced"][0]

    assert overview.current_stage == "Advanced"
    assert overview.readiness_available is True
    assert overview.readiness_target_level == "A2"
    assert overview.next_action == "readiness"
    assert advanced.status == "mastered"


async def test_readiness_unavailable_before_advanced_mastery(postgres_session):
    student_id, language_id = await _student_and_language(postgres_session)

    with pytest.raises(HTTPException) as exc:
        await create_reading_v2_attempt(postgres_session, student_id=student_id, language_id=language_id, mode="readiness")

    assert exc.value.status_code == 409
    overview = await build_reading_v2_overview(postgres_session, student_id=student_id, language_id=language_id)
    assert overview.readiness_available is False
    assert overview.readiness_blocked_reason == "advanced_stage_not_mastered"


async def test_readiness_pass_unlocks_next_cefr_beginner(postgres_session):
    student_id, language_id = await _student_and_language(postgres_session)
    await _move_to_stage(
        postgres_session,
        student_id=student_id,
        language_id=language_id,
        cefr=LanguageLevel.A1,
        stage="Advanced",
        readiness_target=LanguageLevel.A2,
        stage_status="mastered",
    )

    result = await _create_and_submit_readiness(postgres_session, student_id=student_id, language_id=language_id)
    overview = await build_reading_v2_overview(postgres_session, student_id=student_id, language_id=language_id)

    assert result.passed is True
    assert overview.current_cefr == "A2"
    assert overview.current_stage == "Beginner"
    assert overview.readiness_target_level is None


async def test_readiness_fail_keeps_advanced_and_blocks_retake(postgres_session):
    student_id, language_id = await _student_and_language(postgres_session)
    await _move_to_stage(
        postgres_session,
        student_id=student_id,
        language_id=language_id,
        cefr=LanguageLevel.A1,
        stage="Advanced",
        readiness_target=LanguageLevel.A2,
        stage_status="mastered",
    )

    result = await _create_and_submit_readiness(
        postgres_session, student_id=student_id, language_id=language_id, wrong_count=4
    )
    overview = await build_reading_v2_overview(postgres_session, student_id=student_id, language_id=language_id)

    assert result.passed is False
    assert overview.current_cefr == "A1"
    assert overview.current_stage == "Advanced"
    assert overview.readiness_available is False
    assert overview.readiness_blocked_reason == "readiness_retake_requires_more_practice"

    with pytest.raises(HTTPException) as exc:
        await create_reading_v2_attempt(postgres_session, student_id=student_id, language_id=language_id, mode="readiness")
    assert exc.value.status_code == 409


async def test_readiness_retake_blocked_until_3_more_advanced_practice_attempts(monkeypatch, postgres_session):
    _install_unique_mock_generator(monkeypatch)
    student_id, language_id = await _student_and_language(postgres_session)
    await _move_to_stage(
        postgres_session,
        student_id=student_id,
        language_id=language_id,
        cefr=LanguageLevel.A1,
        stage="Advanced",
        readiness_target=LanguageLevel.A2,
        stage_status="mastered",
    )
    await _create_and_submit_readiness(postgres_session, student_id=student_id, language_id=language_id, wrong_count=4)

    for _ in range(2):
        await _create_and_submit_practice(postgres_session, student_id=student_id, language_id=language_id)
    with pytest.raises(HTTPException):
        await create_reading_v2_attempt(postgres_session, student_id=student_id, language_id=language_id, mode="readiness")

    await _create_and_submit_practice(postgres_session, student_id=student_id, language_id=language_id)
    readiness = await create_reading_v2_attempt(postgres_session, student_id=student_id, language_id=language_id, mode="readiness")

    assert readiness.mode == "readiness"
    overview = await build_reading_v2_overview(postgres_session, student_id=student_id, language_id=language_id)
    assert overview.readiness_available is True


async def test_c2_advanced_mastery_marks_final_mastered_state(monkeypatch, postgres_session):
    _install_unique_mock_generator(monkeypatch)
    student_id, language_id = await _student_and_language(postgres_session)
    await _move_to_stage(
        postgres_session,
        student_id=student_id,
        language_id=language_id,
        cefr=LanguageLevel.C2,
        stage="Advanced",
    )

    for _ in range(5):
        await _create_and_submit_practice(postgres_session, student_id=student_id, language_id=language_id)

    overview = await build_reading_v2_overview(postgres_session, student_id=student_id, language_id=language_id)

    assert overview.current_cefr == "C2"
    assert overview.current_stage == "Advanced"
    assert overview.status == "mastered"
    assert overview.readiness_available is False
    assert overview.recent_mastery["readiness"]["blocked_reason"] == "reading_v2_mastered"


async def test_overview_and_path_reflect_readiness_and_locked_states(monkeypatch, postgres_session):
    _install_unique_mock_generator(monkeypatch)
    student_id, language_id = await _student_and_language(postgres_session)
    await _move_to_stage(
        postgres_session,
        student_id=student_id,
        language_id=language_id,
        cefr=LanguageLevel.A1,
        stage="Advanced",
    )

    for _ in range(5):
        await _create_and_submit_practice(postgres_session, student_id=student_id, language_id=language_id)

    overview = await build_reading_v2_overview(postgres_session, student_id=student_id, language_id=language_id)
    path = await build_reading_v2_path(postgres_session, student_id=student_id, language_id=language_id)
    by_stage = {(stage.cefr_level, stage.internal_stage): stage for stage in path.stages}

    assert overview.recent_mastery["readiness"]["available"] is True
    assert by_stage[("A1", "Advanced")].status == "mastered"
    assert by_stage[("A2", "Beginner")].status == "locked"
    assert by_stage[("A2", "Beginner")].recent_mastery["locked_reason"] == "previous_stage_not_mastered"


async def test_readiness_mode_is_stored_separately_from_practice_mode(postgres_session):
    student_id, language_id = await _student_and_language(postgres_session, reading_level=LanguageLevel.A2)
    await _move_to_stage(
        postgres_session,
        student_id=student_id,
        language_id=language_id,
        cefr=LanguageLevel.A2,
        stage="Advanced",
        readiness_target=LanguageLevel.B1,
        stage_status="mastered",
    )

    readiness = await create_reading_v2_attempt(
        postgres_session,
        student_id=student_id,
        language_id=language_id,
        mode="readiness",
    )
    practice = await create_reading_v2_attempt(
        postgres_session,
        student_id=student_id,
        language_id=language_id,
        mode="practice",
    )

    rows = (
        await postgres_session.execute(
            select(LanguageReadingV2Attempt).where(
                LanguageReadingV2Attempt.id.in_([readiness.attempt_id, practice.attempt_id])
            )
        )
    ).scalars().all()
    by_id = {row.id: row for row in rows}
    assert by_id[readiness.attempt_id].mode == "readiness"
    assert by_id[readiness.attempt_id].target_next_cefr == LanguageLevel.B1
    assert by_id[practice.attempt_id].mode == "practice"
    assert by_id[practice.attempt_id].target_next_cefr is None
