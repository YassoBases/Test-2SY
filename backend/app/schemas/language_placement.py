from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PlacementQuestionOut(BaseModel):
    id: int
    section_id: int
    question_type: str
    prompt: dict = Field(default_factory=dict)
    media_url: str | None = None
    max_points: int = 1
    level_hint: str | None = None
    sort_order: int = 0


class PlacementSectionOut(BaseModel):
    id: int
    skill: str
    title_ar: str
    sort_order: int = 0


class PlacementAttemptOut(BaseModel):
    id: int
    language_id: int
    status: str
    started_at: datetime | None = None
    submitted_at: datetime | None = None


class PlacementStartOut(BaseModel):
    attempt: PlacementAttemptOut
    sections: list[PlacementSectionOut] = Field(default_factory=list)
    questions: list[PlacementQuestionOut] = Field(default_factory=list)
    responses_by_question_id: dict[int, dict] = Field(default_factory=dict)


class PlacementSaveResponseIn(BaseModel):
    attempt_id: int
    question_id: int
    response_json: dict = Field(default_factory=dict)


class PlacementSaveResponseOut(BaseModel):
    ok: bool = True


class PlacementSubmitIn(BaseModel):
    attempt_id: int


class PlacementSkillScoreOut(BaseModel):
    skill: str
    score_percent: float
    level: str
    raw_metrics_json: dict | None = None
    ai_evaluation_json: dict | None = None


class PlacementResultsOut(BaseModel):
    assessment_id: int
    overall_level: str | None = None
    overall_calculation_method: str = "bottleneck"
    completed_at: datetime | None = None
    skills: list[PlacementSkillScoreOut] = Field(default_factory=list)
    path_id: int | None = None
    weakest_skill: str | None = None  # the skill that set the bottleneck overall level


class PlacementSpeakingUploadOut(BaseModel):
    ok: bool = True
    media_object_id: int
    public_url: str | None = None

