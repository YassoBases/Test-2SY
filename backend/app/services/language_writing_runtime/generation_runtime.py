"""Writing generation runtime (W6) — connects frozen W0–W5 components with WritingModelProvider."""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.language_generation_gate import can_generate, note_failure, note_success
from app.services.language_writing.enums import OfficialWritingCEFR, WritingGoal
from app.services.language_writing_curriculum.goal_profiles import profile_for_goal
from app.services.language_writing_generation.audit_types import GenerationOutcome
from app.services.language_writing_generation.failure_strategy import DEFAULT_FAILURE_STRATEGY
from app.services.language_writing_generation.generation_pipeline import process_llm_generation
from app.services.language_writing_generation.normalizer_types import WritingLlmRawResponse
from app.services.language_writing_generation.prompt_builder import build_prompt_from_blueprint
from app.services.language_writing_lesson_planner.planner_contract import assemble_blueprint
from app.services.language_writing_lesson_planner.types import LessonPlannerInput
from app.services.language_writing_runtime.errors import WritingRuntimeError, WritingRuntimeErrorCode, WritingRuntimeException
from app.services.language_writing_runtime.model_provider import WritingModelProvider, get_writing_model_provider
from app.services.language_writing_runtime.node_selection import resolve_chain_node
from app.services.language_writing_runtime.persistence import persist_generated_writing_lesson
from app.services.language_writing_runtime.provider_types import WritingModelGenerateRequest
from app.services.language_writing_runtime.types import WritingRuntimeGenerateResult

logger = logging.getLogger(__name__)


def _runtime_error_from_pipeline(*, code: WritingRuntimeErrorCode, message: str) -> WritingRuntimeError:
    return WritingRuntimeError(code=code, message=message, retryable=False)


async def generate_writing_lesson(
    db: AsyncSession | None,
    *,
    language_id: int,
    student_id: int,
    goal: WritingGoal,
    official_cefr: OfficialWritingCEFR,
    chain_id: str,
    node_id: str,
    provider: WritingModelProvider | None = None,
    persist: bool = True,
    locale: str = "en",
    selection_metadata: dict[str, object] | None = None,
) -> WritingRuntimeGenerateResult:
    """Run full writing runtime pipeline for one student lesson."""
    if not can_generate():
        return WritingRuntimeGenerateResult(
            success=False,
            outcome=None,
            blueprint=None,
            pipeline=None,
            canonical_lesson=None,
            audit=None,
            content_item=None,
            provider=None,
            error=WritingRuntimeError(
                code=WritingRuntimeErrorCode.generation_gate_closed,
                message="Generation gate is closed after recent failures",
                retryable=True,
            ),
        )

    node = resolve_chain_node(chain_id=chain_id, node_id=node_id)
    if node is None:
        return WritingRuntimeGenerateResult(
            success=False,
            outcome=None,
            blueprint=None,
            pipeline=None,
            canonical_lesson=None,
            audit=None,
            content_item=None,
            provider=None,
            error=_runtime_error_from_pipeline(
                code=WritingRuntimeErrorCode.blueprint_assembly_failed,
                message=f"Unknown chain/node: {chain_id}/{node_id}",
            ),
        )

    # Wave C: resolver-first grammar context for prompt + persistence stamp.
    from app.services.language_grammar.enums import GrammarEvidenceSourceSkill
    from app.services.language_grammar_skill_context import build_skill_grammar_context

    grammar_ctx = None
    if db is not None:
        grammar_ctx = await build_skill_grammar_context(
            db,
            student_id=student_id,
            language_id=language_id,
            source_skill=GrammarEvidenceSourceSkill.writing,
        )

    planner_result = assemble_blueprint(
        LessonPlannerInput(
            official_cefr=official_cefr,
            goal_profile=profile_for_goal(goal),
            selected_node=node,
            blueprint_id=f"runtime:{student_id}:{chain_id}:{node_id}",
        )
    )
    blueprint = planner_result.blueprint
    prompt_bundle = build_prompt_from_blueprint(blueprint)
    if grammar_ctx is not None:
        from app.services.language_writing_generation.prompt_builder_types import (
            PromptSectionKey,
            WritingPromptBundle,
            WritingPromptSection,
        )

        block = grammar_ctx.prompt_block()
        new_sections: list[WritingPromptSection] = []
        for section in prompt_bundle.sections:
            if section.key == PromptSectionKey.grammar:
                new_sections.append(
                    WritingPromptSection(
                        key=PromptSectionKey.grammar,
                        content=f"{block}\n\n{section.content}".strip(),
                    )
                )
            else:
                new_sections.append(section)
        prompt_bundle = WritingPromptBundle(
            sections=tuple(new_sections),
            blueprint_id=prompt_bundle.blueprint_id,
            blueprint_version=prompt_bundle.blueprint_version,
            blueprint_hash=prompt_bundle.blueprint_hash,
            builder_version=prompt_bundle.builder_version,
        )
    model_provider = provider or get_writing_model_provider()
    provider_info = model_provider.info()

    max_attempts = DEFAULT_FAILURE_STRATEGY.max_llm_retries + 1
    pipeline_result = None
    provider_response = None
    attempts = 0
    last_error: WritingRuntimeError | None = None

    for attempt in range(max_attempts):
        attempts = attempt + 1
        try:
            provider_response = await model_provider.generate(
                WritingModelGenerateRequest(prompt_bundle=prompt_bundle, locale=locale)
            )
        except WritingRuntimeException as exc:
            last_error = exc.error
            note_failure()
            if exc.error.retryable and attempt + 1 < max_attempts:
                continue
            return WritingRuntimeGenerateResult(
                success=False,
                outcome=None,
                blueprint=blueprint,
                pipeline=None,
                canonical_lesson=None,
                audit=None,
                content_item=None,
                provider=provider_info,
                error=exc.error,
                attempts=attempts,
            )

        raw = WritingLlmRawResponse(
            raw_text=provider_response.raw_text,
            llm_version=provider_response.llm_version,
        )
        pipeline_result = process_llm_generation(
            blueprint,
            prompt_bundle,
            raw,
            generation_duration_ms=provider_response.duration_ms,
            attempt_repair=True,
        )

        if pipeline_result.success:
            note_success()
            break

        if (
            pipeline_result.normalization.success is False
            and DEFAULT_FAILURE_STRATEGY.retry_on_normalization_failure
            and attempt + 1 < max_attempts
        ):
            last_error = _runtime_error_from_pipeline(
                code=WritingRuntimeErrorCode.malformed_json,
                message="LLM output failed normalization — retrying",
            )
            continue
        break

    if pipeline_result is None or provider_response is None:
        return WritingRuntimeGenerateResult(
            success=False,
            outcome=None,
            blueprint=blueprint,
            pipeline=pipeline_result,
            canonical_lesson=None,
            audit=None,
            content_item=None,
            provider=provider_info,
            error=last_error
            or _runtime_error_from_pipeline(
                code=WritingRuntimeErrorCode.provider_error,
                message="Generation did not produce a pipeline result",
            ),
            attempts=attempts,
        )

    if not pipeline_result.success or pipeline_result.canonical_lesson is None:
        code = WritingRuntimeErrorCode.validation_failure
        message = "Lesson validation failed after repair"
        if not pipeline_result.normalization.success:
            code = WritingRuntimeErrorCode.malformed_json
            message = "LLM output could not be normalized"
        elif pipeline_result.repair and pipeline_result.repair.repaired:
            code = WritingRuntimeErrorCode.repair_failure
            message = "Repair applied but validation still failed"
        note_failure()
        return WritingRuntimeGenerateResult(
            success=False,
            outcome=pipeline_result.outcome,
            blueprint=blueprint,
            pipeline=pipeline_result,
            canonical_lesson=None,
            audit=pipeline_result.audit,
            content_item=None,
            provider=provider_info,
            error=_runtime_error_from_pipeline(code=code, message=message),
            attempts=attempts,
        )

    content_item = None
    if persist and db is not None:
        try:
            stamp_meta = dict(selection_metadata or {})
            if grammar_ctx is not None:
                stamp_meta.update(grammar_ctx.as_stamp_dict())
            content_item = await persist_generated_writing_lesson(
                db,
                language_id=language_id,
                student_id=student_id,
                blueprint=blueprint,
                canonical=pipeline_result.canonical_lesson,
                audit=pipeline_result.audit,
                model_name=provider_response.model_name,
                provider_name=provider_response.provider_name,
                selection_metadata=stamp_meta or None,
            )
            # Wave D: issue attested activity session bound to this writing item.
            if grammar_ctx is not None and content_item is not None:
                from app.services.language_grammar.enums import GrammarEvidenceSourceSkill
                from app.services.language_grammar_integrity import issue_and_stamp_for_context

                session = await issue_and_stamp_for_context(
                    db,
                    student_id=student_id,
                    language_id=language_id,
                    grammar_ctx=grammar_ctx,
                    skill=GrammarEvidenceSourceSkill.writing,
                    activity_type="writing",
                    lesson_id=str(content_item.id),
                    content_item_id=int(content_item.id),
                    server_payload={
                        "min_words": int(blueprint.success_criteria.min_words),
                        "content_item_id": int(content_item.id),
                    },
                )
                body = dict(content_item.body_json or {})
                body["activity_session_id"] = str(session.id)
                content_item.body_json = body
                from sqlalchemy.orm.attributes import flag_modified

                flag_modified(content_item, "body_json")
                await db.flush()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to persist writing lesson")
            note_failure()
            return WritingRuntimeGenerateResult(
                success=False,
                outcome=pipeline_result.outcome,
                blueprint=blueprint,
                pipeline=pipeline_result,
                canonical_lesson=pipeline_result.canonical_lesson,
                audit=pipeline_result.audit,
                content_item=None,
                provider=provider_info,
                error=WritingRuntimeError(
                    code=WritingRuntimeErrorCode.persistence_failed,
                    message=str(exc),
                    retryable=False,
                ),
                attempts=attempts,
            )

    return WritingRuntimeGenerateResult(
        success=True,
        outcome=pipeline_result.outcome,
        blueprint=blueprint,
        pipeline=pipeline_result,
        canonical_lesson=pipeline_result.canonical_lesson,
        audit=pipeline_result.audit,
        content_item=content_item,
        provider=provider_info,
        error=(
            WritingRuntimeError(
                code=WritingRuntimeErrorCode.repair_success,
                message="Lesson generated after structural repair",
                retryable=False,
            )
            if pipeline_result.outcome == GenerationOutcome.soft_failure
            else None
        ),
        attempts=attempts,
    )
