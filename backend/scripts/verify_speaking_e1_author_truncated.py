"""Regression: stop_reason=max_tokens returns author_truncated (not generation_failed)."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.services.language_educational_package.pipeline import GenerationOutcome
from app.services.language_speaking_educational_package.claude_author import (
    AUTHOR_PROVIDER_CLAUDE,
    ClaudeAuthorResult,
)
from app.services.language_speaking_educational_package.author_pipeline import (
    generate_speaking_learning_package,
)
from app.services.language_speaking_educational_package_api.service import (
    SpeakingLearningPackageApiError,
    create_speaking_learning_package_api,
)


CONSTRAINTS = {
    "skill": "speaking",
    "official_cefr": "A2",
    "learning_stage": 1,
    "mission_id": "spk-mis-test",
    "mission_kind": "teaching",
    "execution_mode": "study",
    "evidence_intent": "none",
    "blueprint_id": "spk-bp-test",
    "blueprint_hash": "abc",
    "learning_focus": "Travel greetings",
    "objectives": ["Speak clearly"],
    "vocabulary_ids": ["lex_a"],
    "vocabulary_surface_forms": ["Welcome to"],
    "grammar_topic_ids": [],
    "teaching_block_specs": [],
    "weak_skill_labels": ["Travel greetings"],
    "difficulty": "standard",
    "scenario_type": "conversation",
    "input_material_kind": "dialogue",
    "lesson_length_band": "standard",
    "question_ladder_policy": {
        "required_bands": ["literal", "vocabulary", "reasoning", "personal_opinion", "personal_experience"],
        "min_steps": 5,
        "max_steps": 7,
    },
    "evidence_slot_plan": [],
    "reflection_requirements": {"prompt_count": 2},
    "forbidden_behaviors": [],
    "locale": "en",
    "mini_practice_task_id": "task_test",
    "schema_version": "2.0.0",
}


def _truncated_author() -> ClaudeAuthorResult:
    return ClaudeAuthorResult(
        text='```json\n{"input_material": {',
        model="claude-sonnet-5",
        stop_reason="max_tokens",
        input_tokens=3929,
        output_tokens=8000,
        provider=AUTHOR_PROVIDER_CLAUDE,
    )


async def _run() -> None:
    db = AsyncMock()
    truncated = _truncated_author()

    with patch(
        "app.services.language_speaking_educational_package.author_pipeline.author_package_json_claude",
        new=AsyncMock(return_value=truncated),
    ), patch(
        "app.services.language_speaking_educational_package.author_pipeline.find_cached_package_item",
        new=AsyncMock(return_value=None),
    ), patch(
        "app.services.language_speaking_educational_package.author_pipeline.process_package_generation",
    ) as process_mock:
        result = await generate_speaking_learning_package(
            db,
            student_id=103,
            language_id=1,
            constraints_payload=CONSTRAINTS,
            author_mode="claude",
            use_cache=False,
        )
        assert process_mock.call_count == 0, "must not enter normalize/pipeline on truncation"

    assert result.success is False
    assert result.reason == "author_truncated"
    assert result.reason != "generation_failed"
    assert result.outcome == GenerationOutcome.hard_failure
    assert result.audit["stop_reason"] == "max_tokens"
    assert result.audit["output_tokens"] == 8000
    assert result.audit["model"] == "claude-sonnet-5"
    assert result.audit["input_tokens"] == 3929
    assert result.audit["provider"] == AUTHOR_PROVIDER_CLAUDE

    with patch(
        "app.services.language_speaking_educational_package_api.service.generate_speaking_learning_package",
        new=AsyncMock(return_value=result),
    ):
        try:
            await create_speaking_learning_package_api(
                db,
                student_id=103,
                language_id=1,
                constraints=CONSTRAINTS,
                author_mode="claude",
                use_cache=False,
            )
            raise AssertionError("expected SpeakingLearningPackageApiError")
        except SpeakingLearningPackageApiError as exc:
            assert exc.status_code == 422
            assert isinstance(exc.detail, dict)
            assert exc.detail == {
                "reason": "author_truncated",
                "stop_reason": "max_tokens",
                "output_tokens": 8000,
                "model": "claude-sonnet-5",
            }

    print("PASS author_truncated observable")


if __name__ == "__main__":
    asyncio.run(_run())
