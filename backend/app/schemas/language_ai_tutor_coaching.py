"""Student Conversational Coaching API schemas (Wave E2)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CoachingStatusOut(BaseModel):
    enabled: bool


class CoachingTurnIn(BaseModel):
    message: str = ""
    session_id: str | None = None
    conversation_id: str | None = None
    grammar_id: str | None = None
    lesson_id: str | None = None
    activity_id: str | None = None
    step_id: str | None = None
    student_attempt: str | None = None
    is_correct: bool | None = None
    request_full_answer: bool = False
    request_wrap_up: bool = False
    student_language: str = "en"


class CoachingWrapUpOut(BaseModel):
    todays_grammar: str = ""
    grammar_id: str = ""
    common_mistakes: list[str] = Field(default_factory=list)
    strong_performance: list[str] = Field(default_factory=list)
    suggested_review: str = ""
    next_lesson_preview: str = ""
    summary_text: str = ""


class CoachingTurnOut(BaseModel):
    utterance: str
    move: str
    hint_level: str | None = None
    explanation_variety: str = "step_by_step"
    diagnosis_kind: str | None = None
    diagnosis_why: str = ""
    reflection_question: str = ""
    motivation_line: str = ""
    explainability_note: str = ""
    reasons: list[str] = Field(default_factory=list)
    session_id: str = ""
    grammar_id: str | None = None
    provider: str = "template_fallback"
    wrap_up: CoachingWrapUpOut | None = None
    safety_code: str = "ok"
    schema_version: int = 1
