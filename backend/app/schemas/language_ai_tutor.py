"""Student AI Tutor Foundation API schemas (Wave E1)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AiTutorStatusOut(BaseModel):
    enabled: bool


class AiTutorTurnIn(BaseModel):
    message: str = ""
    prompt_kind: str = "answer_question"
    conversation_id: str | None = None
    grammar_id: str | None = None
    lesson_id: str | None = None
    activity_id: str | None = None
    step_id: str | None = None
    student_language: str = "en"
    persona_id: str | None = None


class AiTutorTurnOut(BaseModel):
    utterance: str
    prompt_kind: str
    grammar_id: str | None = None
    explanation_style: str = "guided"
    explainability_note: str = ""
    safety_code: str = "ok"
    provider: str = "template_fallback"
    conversation_id: str = ""
    context_as_of: str = ""
    schema_version: int = 1


class AiTutorContextOut(BaseModel):
    enabled: bool = False
    student_id: int
    language_id: int = 1
    as_of: str = ""
    safety_code: str = "ok"
    safety_message: str = ""
    grammar_id: str | None = None
    display_name: str = ""
    explanation_style: str = "guided"
    explainability_note: str = ""
    curriculum_version: str = ""
    session: dict = Field(default_factory=dict)
    teacher_persona: dict = Field(default_factory=dict)
    adaptive: dict = Field(default_factory=dict)
