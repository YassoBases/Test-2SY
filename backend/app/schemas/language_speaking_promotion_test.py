"""API schemas for Speaking Promotion Assessment (SPA) — S18/S19 student-safe surfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SpeakingPromotionAssessmentStatusOut(BaseModel):
    available: bool
    spa_unlocked: bool
    source_cefr: str | None = None
    target_cefr: str | None = None
    estimated_duration_seconds: int = 0
    status: str = "unavailable"
    assessment_id: str | None = None
    blueprint_id: str | None = None
    attempt_id: str | None = None
    task_count: int = 0
    has_interaction_coverage_gaps: bool = False
    message: str = ""


class SpeakingPromotionAssessmentTaskOut(BaseModel):
    task_id: str
    task_order: int
    task_family: str
    execution_mode: str
    scenario: str
    student_prompt: str
    follow_up_prompts: list[str] = Field(default_factory=list)
    context_descriptor: str = ""
    max_duration_seconds: int = 0
    preparation_seconds: int = 0
    spontaneous_production_required: bool = False
    spontaneous_interaction_required: bool = False


class SpeakingPromotionAssessmentCreateOut(BaseModel):
    assessment_id: str
    blueprint_id: str
    status: str
    source_cefr: str
    target_cefr: str
    task_count: int
    frozen: bool
    has_interaction_coverage_gaps: bool = False
    tasks: list[SpeakingPromotionAssessmentTaskOut] = Field(default_factory=list)
    attempt_id: str | None = None


class SpeakingPromotionAssessmentGetOut(BaseModel):
    assessment_id: str
    blueprint_id: str
    status: str
    source_cefr: str
    target_cefr: str
    task_count: int
    frozen: bool
    has_interaction_coverage_gaps: bool = False
    tasks: list[SpeakingPromotionAssessmentTaskOut] = Field(default_factory=list)
    created_at: str = ""
    attempt_id: str | None = None
    current_task_index: int | None = None
    ready_for_official_promotion: bool = False


class SpeakingPromotionAssessmentStartOut(BaseModel):
    assessment_id: str
    blueprint_id: str
    attempt_id: str
    session_id: str
    status: str
    current_task_index: int = 0
    current_task: SpeakingPromotionAssessmentTaskOut | None = None
    task_count: int = 0
    resumed: bool = False


class SpeakingPromotionAssessmentSubmitIn(BaseModel):
    task_id: str
    transcript_text: str = ""
    media_object_id: str | None = None
    attempt_id: str | None = None


class SpeakingPromotionAssessmentSubmitOut(BaseModel):
    assessment_id: str
    attempt_id: str
    task_id: str
    status: str
    current_task_index: int | None = None
    next_task_id: str | None = None
    all_tasks_complete: bool = False
    student_safe_summary: str = ""
    idempotent: bool = False


class SpeakingPromotionAssessmentBridgeOut(BaseModel):
    focus_skill_ids: list[str] = Field(default_factory=list)
    focus_labels: list[str] = Field(default_factory=list)
    summary: str = ""
    suggested_practice: list[str] = Field(default_factory=list)


class SpeakingPromotionAssessmentResultOut(BaseModel):
    assessment_id: str
    blueprint_id: str
    attempt_id: str
    outcome: str
    status: str
    ready_for_official_promotion: bool = False
    message: str = ""
    blocked_by_required_competency: bool = False
    bridge_recommendation: SpeakingPromotionAssessmentBridgeOut | None = None
    completed_at: str = ""


class SpeakingPromotionAssessmentCompleteOut(SpeakingPromotionAssessmentResultOut):
    pass
