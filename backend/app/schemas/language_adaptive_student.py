"""Student Adaptive Intelligence API schemas (Phase 2)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AdaptiveStatusOut(BaseModel):
    enabled: bool


class AdaptiveDifficultyOut(BaseModel):
    grammar_id: str
    difficulty_level: str
    vocabulary_richness: str
    sentence_length: str
    distractor_quality: str
    reading_complexity: str
    listening_speed: str
    writing_expectations: str
    reasons: list[str] = Field(default_factory=list)


class AdaptiveReviewOut(BaseModel):
    grammar_id: str
    display_name: str = ""
    horizon: str
    urgency: float = 0.0
    explanation: str = ""
    reasons: list[str] = Field(default_factory=list)


class AdaptiveRemediationOut(BaseModel):
    grammar_id: str
    kind: str
    display_name: str = ""
    explanation: str = ""
    reasons: list[str] = Field(default_factory=list)


class AdaptiveSignalOut(BaseModel):
    kind: str
    grammar_id: str
    display_name: str = ""
    severity: float = 0.0
    reasons: list[str] = Field(default_factory=list)


class AdaptiveProfileOut(BaseModel):
    preferred_pace: str = "steady"
    preferred_explanation_depth: str = "guided"
    preferred_examples: str = "everyday"
    weak_grammar_ids: list[str] = Field(default_factory=list)
    strong_grammar_ids: list[str] = Field(default_factory=list)
    average_confidence: float = 0.0
    preferred_activity_types: list[str] = Field(default_factory=list)
    learning_streak_days: int = 0
    engagement_score: float = 0.0


class AdaptiveTeacherOut(BaseModel):
    struggling_topics: list[str] = Field(default_factory=list)
    strength_skills: list[str] = Field(default_factory=list)
    risk_notes: list[str] = Field(default_factory=list)
    focus_grammar_id: str | None = None
    focus_display_name: str = ""
    explanations: list[str] = Field(default_factory=list)
    advisory_only: bool = True


class AdaptiveParentOut(BaseModel):
    mastered_percent: float = 0.0
    cefr_band: str = ""
    current_focus: str = ""
    current_focus_grammar_id: str | None = None
    recommended_minutes: int = 15
    recommendation_text: str = ""
    summary: str = ""
    explanations: list[str] = Field(default_factory=list)
    advisory_only: bool = True


class AdaptiveInsightsOut(BaseModel):
    enabled: bool = False
    student_id: int
    language_id: int = 1
    as_of: str = ""
    current_grammar_id: str | None = None
    profile: AdaptiveProfileOut = Field(default_factory=AdaptiveProfileOut)
    difficulty: AdaptiveDifficultyOut | None = None
    review_recommendations: list[AdaptiveReviewOut] = Field(default_factory=list)
    activity_mix: dict[str, float] = Field(default_factory=dict)
    activity_mix_reasons: list[str] = Field(default_factory=list)
    remediations: list[AdaptiveRemediationOut] = Field(default_factory=list)
    signals: list[AdaptiveSignalOut] = Field(default_factory=list)
    teacher: AdaptiveTeacherOut = Field(default_factory=AdaptiveTeacherOut)
    parent: AdaptiveParentOut = Field(default_factory=AdaptiveParentOut)
    schema_version: int = 1
