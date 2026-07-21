"""Map S7 evaluation results into SPA task score summaries (API layer).

S7 remains the per-task evaluator; promotion_test owns aggregate/mandatory gates.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.services.language_speaking_evaluator.engine import evaluate_speaking_turn, new_evaluation_context
from app.services.language_speaking_evaluator.evaluation_result import SpeakingEvaluationEngineResult
from app.services.language_speaking_evaluator.input_types import (
    SpeakingEvaluationInput,
    SpeakingGoalContext,
    SpeakingOfficialCefrContext,
    SpeakingTaskContext,
)
from app.services.language_speaking_evaluation_runtime.knowledge_bridge import (
    apply_speaking_evaluation_to_knowledge_model,
)
from app.services.language_speaking_knowledge_model.types import ObservationSourceType
from app.services.language_speaking_promotion_test import (
    EVIDENCE_SOURCE_PROMOTION_ASSESSMENT,
    SpaTaskScoreSummary,
    SpeakingPromotionAssessmentTask,
)
from sqlalchemy.ext.asyncio import AsyncSession


def spa_task_to_speaking_task_context(task: SpeakingPromotionAssessmentTask) -> SpeakingTaskContext:
    er = task.evaluator_requirements
    return SpeakingTaskContext(
        task_id=task.task_id,
        task_type=er.task_type,
        task_prompt=task.student_prompt,
        task_instructions=task.scenario or task.context_descriptor,
        success_criteria=er.success_criteria,
        target_skill_ids=er.target_skill_ids,
    )


def score_summary_from_s7(
    evaluation: SpeakingEvaluationEngineResult,
    *,
    task: SpeakingPromotionAssessmentTask,
    media_object_id: str | None = None,
) -> SpaTaskScoreSummary:
    return SpaTaskScoreSummary(
        task_id=task.task_id,
        task_order=task.task_order,
        task_family=task.task_family.value,
        evaluation_id=evaluation.evaluation_id,
        overall_readiness=float(evaluation.overall_readiness),
        completion_eligible=bool(evaluation.completion_eligibility.eligible),
        semantic_task_met=bool(evaluation.completion_eligibility.semantic_task_met),
        target_skill_ids=task.target_skill_ids,
        interaction_claim_allowed=False,
        evidence_source=EVIDENCE_SOURCE_PROMOTION_ASSESSMENT,
        media_object_id=media_object_id,
        student_safe_summary=str(evaluation.explanation.summary or "")[:280],
        priority_issue=str(evaluation.priority_issue or ""),
        weak_skills=tuple(str(x) for x in evaluation.weak_skills),
        strong_skills=tuple(str(x) for x in evaluation.strong_skills),
    )


async def evaluate_spa_task_with_s7(
    *,
    db: AsyncSession | None,
    student_id: int,
    language_id: int,
    official_cefr: str,
    session_id: str,
    attempt_id: str,
    task: SpeakingPromotionAssessmentTask,
    transcript_text: str,
    media_object_id: str | None = None,
    quarantine_apply: bool = True,
) -> tuple[SpaTaskScoreSummary, SpeakingEvaluationEngineResult]:
    """Evaluate one SPA task via S7; quarantine knowledge-bridge apply by default."""
    tokens = tuple((transcript_text or "").lower().split())
    eval_input = SpeakingEvaluationInput(
        transcript_text=transcript_text or "",
        transcript_word_count=len(tokens),
        transcript_tokens=tokens,
        evidence_availability={"transcript": bool(transcript_text)},
        evidence_reliability=0.7 if transcript_text else 0.0,
    )
    task_ctx = spa_task_to_speaking_task_context(task)
    evaluation_id = f"spa-eval-{uuid.uuid4().hex[:12]}"
    context = new_evaluation_context(
        evaluation_id=evaluation_id,
        student_id=student_id,
        language_id=language_id,
        session_id=session_id,
        task_id=task.task_id,
        attempt_id=attempt_id,
        revision_number=1,
        task=task_ctx,
        goal=SpeakingGoalContext(
            speaking_goal="speaking_promotion_assessment",
            goal_label="Speaking promotion assessment",
        ),
        official_cefr=SpeakingOfficialCefrContext(official_cefr=official_cefr),
        evaluated_at=datetime.now(timezone.utc).isoformat(),
    )
    evaluation = await evaluate_speaking_turn(eval_input, context)

    if quarantine_apply and db is not None:
        # Explicit quarantine path — must not mutate S2 mastery.
        await apply_speaking_evaluation_to_knowledge_model(
            db,
            student_id=student_id,
            language_id=language_id,
            evaluation=evaluation,
            turn_reference=f"spa:{attempt_id}:{task.task_id}",
            session_id=session_id,
            source_type=ObservationSourceType.promotion_assessment,
        )

    return score_summary_from_s7(evaluation, task=task, media_object_id=media_object_id), evaluation
