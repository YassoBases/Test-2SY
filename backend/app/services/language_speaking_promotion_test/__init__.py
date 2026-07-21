"""Speaking promotion_test — SPA blueprint (S18) + assessment execution (S19).

RESPONSIBILITY:
  S18 — specification, validation, frozen blueprint, bounded persistence, unlock reconcile
  S19 — distinct assessment/attempt identities, session lifecycle, aggregate+mandatory
        PASS gates, FAIL bridge projection, evidence quarantine label

Does NOT write official_speaking_cefr (S20), apply S8 mastery by default, host
SpeakingLearningSession, or invent live/EVI SPA tasks.
"""

from app.services.language_speaking_promotion_test.assessment import (
    build_speaking_promotion_assessment,
    mint_assessment_id,
    mint_attempt_id,
    mint_session_id,
)
from app.services.language_speaking_promotion_test.builder import build_spa_blueprint
from app.services.language_speaking_promotion_test.engine import create_speaking_promotion_assessment
from app.services.language_speaking_promotion_test.execution import (
    abandon_speaking_promotion_assessment,
    complete_speaking_promotion_assessment,
    current_task_id,
    record_task_score,
    start_speaking_promotion_assessment,
    timeout_speaking_promotion_assessment,
)
from app.services.language_speaking_promotion_test.execution_types import (
    LANGUAGE_SPEAKING_PROMOTION_EXECUTION_VERSION,
    MAX_ATTEMPT_HISTORY,
    SpaAggregatePerformance,
    SpaAssessmentAttempt,
    SpaAssessmentOutcome,
    SpaAssessmentResult,
    SpaAssessmentSession,
    SpaBridgeRecommendation,
    SpaExecutionFailureCode,
    SpaExecutionResult,
    SpaMandatoryCompetencyKind,
    SpaMandatoryCompetencyOutcome,
    SpaMandatoryCompetencyRequirement,
    SpaPassGateDecision,
    SpaTaskAttempt,
    SpaTaskAttemptStatus,
    SpaTaskScoreSummary,
    SpeakingPromotionAssessment,
)
from app.services.language_speaking_promotion_test.mandatory import (
    declare_mandatory_competency_requirements,
)
from app.services.language_speaking_promotion_test.outcome import (
    build_assessment_result,
    decide_spa_pass_gate,
    evaluate_aggregate_performance,
    evaluate_mandatory_competencies,
)
from app.services.language_speaking_promotion_test.policy import (
    EVIDENCE_SOURCE_PROMOTION_ASSESSMENT,
    MAX_PERSISTED_BLUEPRINTS,
    SPA_POLICY_VERSION,
    SPA_REQUIRES_INTERACTION_EVIDENCE,
    SPA_SCHEMA_VERSION,
    SpaCapabilityKind,
    SpaExecutionMode,
    SpaSkillEvaluatorCompatibility,
    SpaTaskFamily,
    classify_skill_evaluator_compatibility,
    skill_requires_interactive_evaluation,
)
from app.services.language_speaking_promotion_test.quarantine import (
    is_promotion_assessment_evidence_source,
    spa_evidence_may_apply_to_mastery,
)
from app.services.language_speaking_promotion_test.specification import (
    SpaSpecificationError,
    build_speaking_promotion_assessment_specification,
)
from app.services.language_speaking_promotion_test.storage import (
    SPEAKING_PROMOTION_ASSESSMENTS_KEY,
    assert_bucket_bounded,
    assessments_bucket_from_payload,
    count_persisted_blueprints,
    find_assessment_in_payload,
    get_active_assessment,
    get_active_blueprint,
    mark_active_terminal,
    merge_assessments_into_payload,
    persist_active_assessment,
    persist_active_blueprint,
)
from app.services.language_speaking_promotion_test.types import (
    LANGUAGE_SPEAKING_PROMOTION_TEST_VERSION,
    SpaAssessmentCoverageGap,
    SpaBlueprintStatus,
    SpaCreateFailureCode,
    SpaCreateResult,
    SpaUnlockAuthority,
    SpeakingPromotionAssessmentBlueprint,
    SpeakingPromotionAssessmentSpecification,
    SpeakingPromotionAssessmentTask,
    SpeakingPromotionTestBundle,
)
from app.services.language_speaking_promotion_test.unlock import (
    reconcile_spa_unlock,
    resolve_next_speaking_cefr_local,
)
from app.services.language_speaking_promotion_test.validation import (
    validate_spa_blueprint,
    validate_spa_tasks_against_specification,
)

__all__ = [
    "EVIDENCE_SOURCE_PROMOTION_ASSESSMENT",
    "LANGUAGE_SPEAKING_PROMOTION_EXECUTION_VERSION",
    "LANGUAGE_SPEAKING_PROMOTION_TEST_VERSION",
    "MAX_ATTEMPT_HISTORY",
    "MAX_PERSISTED_BLUEPRINTS",
    "SPA_POLICY_VERSION",
    "SPA_REQUIRES_INTERACTION_EVIDENCE",
    "SPA_SCHEMA_VERSION",
    "SPEAKING_PROMOTION_ASSESSMENTS_KEY",
    "SpaAggregatePerformance",
    "SpaAssessmentAttempt",
    "SpaAssessmentCoverageGap",
    "SpaAssessmentOutcome",
    "SpaAssessmentResult",
    "SpaAssessmentSession",
    "SpaBlueprintStatus",
    "SpaBridgeRecommendation",
    "SpaCapabilityKind",
    "SpaCreateFailureCode",
    "SpaCreateResult",
    "SpaExecutionFailureCode",
    "SpaExecutionMode",
    "SpaExecutionResult",
    "SpaMandatoryCompetencyKind",
    "SpaMandatoryCompetencyOutcome",
    "SpaMandatoryCompetencyRequirement",
    "SpaPassGateDecision",
    "SpaSkillEvaluatorCompatibility",
    "SpaSpecificationError",
    "SpaTaskAttempt",
    "SpaTaskAttemptStatus",
    "SpaTaskFamily",
    "SpaTaskScoreSummary",
    "SpaUnlockAuthority",
    "SpeakingPromotionAssessment",
    "SpeakingPromotionAssessmentBlueprint",
    "SpeakingPromotionAssessmentSpecification",
    "SpeakingPromotionAssessmentTask",
    "SpeakingPromotionTestBundle",
    "abandon_speaking_promotion_assessment",
    "assert_bucket_bounded",
    "assessments_bucket_from_payload",
    "build_assessment_result",
    "build_spa_blueprint",
    "build_speaking_promotion_assessment",
    "build_speaking_promotion_assessment_specification",
    "classify_skill_evaluator_compatibility",
    "complete_speaking_promotion_assessment",
    "count_persisted_blueprints",
    "create_speaking_promotion_assessment",
    "current_task_id",
    "decide_spa_pass_gate",
    "declare_mandatory_competency_requirements",
    "evaluate_aggregate_performance",
    "evaluate_mandatory_competencies",
    "find_assessment_in_payload",
    "get_active_assessment",
    "get_active_blueprint",
    "is_promotion_assessment_evidence_source",
    "mark_active_terminal",
    "merge_assessments_into_payload",
    "mint_assessment_id",
    "mint_attempt_id",
    "mint_session_id",
    "persist_active_assessment",
    "persist_active_blueprint",
    "reconcile_spa_unlock",
    "record_task_score",
    "resolve_next_speaking_cefr_local",
    "skill_requires_interactive_evaluation",
    "spa_evidence_may_apply_to_mastery",
    "start_speaking_promotion_assessment",
    "timeout_speaking_promotion_assessment",
    "validate_spa_blueprint",
    "validate_spa_tasks_against_specification",
]
