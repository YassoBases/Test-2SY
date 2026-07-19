from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select

from app.models.language.analytics import LanguageAnalytics
from app.models.language.catalog import Language
from app.models.language.enums import LanguageLevel
from app.models.language.reading_v2 import LanguageReadingV2Attempt, LanguageReadingV2StudentState
from app.models.user import User, UserRole
from app.schemas.language_reading_v2 import GenerationBlueprint
from app.services.language_reading_v2_service import (
    CEFR_LEVELS,
    INTERNAL_STAGES,
    build_generation_blueprint,
    build_reading_v2_overview,
    build_reading_v2_path,
    create_reading_v2_attempt,
    generate_reading_activity_from_blueprint,
    score_generated_activity,
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
        "prompt_version": "reading_v2_r1",
    }
    values.update(overrides)
    return GenerationBlueprint(**values)


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


async def test_attempt_creation_stores_snapshots_and_strips_student_keys(postgres_session):
    student_id, language_id = await _student_and_language(postgres_session, reading_level=LanguageLevel.A2)

    out = await create_reading_v2_attempt(postgres_session, student_id=student_id, language_id=language_id)

    stored = (
        await postgres_session.execute(
            select(LanguageReadingV2Attempt).where(LanguageReadingV2Attempt.id == out.attempt_id)
        )
    ).scalar_one()
    assert stored.generation_blueprint_json["cefr_level"] == "A2"
    assert stored.generated_activity_json["questions"]
    assert stored.validation_result_json["valid"] is True
    assert all("answer_key" not in question for question in out.activity["questions"])
    assert "accepted_answers" not in str(out.activity)
    assert "required_key_terms" not in str(out.activity)


async def test_xp_alone_does_not_progress_stage(postgres_session):
    student_id, language_id = await _student_and_language(postgres_session)

    await build_reading_v2_overview(postgres_session, student_id=student_id, language_id=language_id)
    path = await build_reading_v2_path(postgres_session, student_id=student_id, language_id=language_id)

    current = [stage for stage in path.stages if stage.status == "current"]
    assert [(stage.cefr_level, stage.internal_stage) for stage in current] == [("A1", "Beginner")]


async def test_insufficient_evidence_does_not_progress_stage(postgres_session):
    student_id, language_id = await _student_and_language(postgres_session)
    attempt = await create_reading_v2_attempt(postgres_session, student_id=student_id, language_id=language_id)
    answers = {
        "q1": {"choice_id": "a"},
        "q2": True,
        "q3": "margin",
        "q4": "checks the title",
    }

    await submit_reading_v2_attempt(
        postgres_session,
        student_id=student_id,
        language_id=language_id,
        attempt_id=attempt.attempt_id,
        answers=answers,
    )
    overview = await build_reading_v2_overview(postgres_session, student_id=student_id, language_id=language_id)

    assert overview.current_cefr == "A1"
    assert overview.current_stage == "Beginner"
    assert overview.recent_mastery["evidence_sufficient"] is False


async def test_readiness_mode_is_stored_separately_from_practice_mode(postgres_session):
    student_id, language_id = await _student_and_language(postgres_session, reading_level=LanguageLevel.A2)

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
