"""AI Tutor Foundation contracts (Wave E1).

Orchestration / communication only — never educational source of truth.
LLM receives projected TutorContext dicts, never raw DB/engine models.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.services.language_ai_tutor.enums import (
    ExplanationStyle,
    TutorPromptKind,
    TutorSafetyCode,
)
from app.services.language_grammar_activity_authoring.types import TeacherPersona

AI_TUTOR_SCHEMA_VERSION = 1
AI_TUTOR_JSONB_NAMESPACE = "ai_tutor"
AI_TUTOR_PACKAGE = "language_ai_tutor"


@dataclass(frozen=True, slots=True)
class TutorSessionAwareness:
    """Read-only lesson session projection — never mutates runtime."""

    lesson_id: str = ""
    lesson_objective: str = ""
    grammar_id: str = ""
    current_activity_id: str = ""
    current_step_id: str = ""
    completed_activity_ids: tuple[str, ...] = ()
    remaining_activity_ids: tuple[str, ...] = ()
    runtime_state: str = ""


@dataclass(frozen=True, slots=True)
class TutorGrammarSurface:
    """Authoritative grammar focus for this tutor turn (from resolver/runtime/progression)."""

    grammar_id: str
    display_code: str = ""
    display_name: str = ""
    cefr_band: str = ""
    teaching_notes: str = ""
    examples: tuple[str, ...] = ()
    common_mistakes: tuple[str, ...] = ()
    learning_objectives: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class TutorAdaptiveSurface:
    """Projected adaptive advice — copied fields only; never live engine objects."""

    preferred_pace: str = "steady"
    preferred_explanation_depth: str = "guided"
    preferred_examples: str = "everyday"
    average_confidence: float = 0.0
    weak_grammar_ids: tuple[str, ...] = ()
    strong_grammar_ids: tuple[str, ...] = ()
    difficulty_level: str = "normal"
    learning_confidence_current: float | None = None
    mastery_score_current: float | None = None
    review_horizons: tuple[str, ...] = ()
    weakness_signal_kinds: tuple[str, ...] = ()
    remediation_kinds: tuple[str, ...] = ()
    activity_mix: dict[str, float] = field(default_factory=dict)
    explainability_notes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class TutorMemorySummary:
    """Compact conversation memory projection for prompts."""

    preferred_tone: str = "supportive"
    preferred_examples: str = "everyday"
    explanation_preference: str = "guided"
    recurring_questions: tuple[str, ...] = ()
    unfinished_discussion: str = ""
    recent_turn_summaries: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class TutorContext:
    """Read-only context assembled before every tutor response."""

    student_id: int
    language_id: int
    as_of: str
    student_language: str = "en"
    curriculum_version: str = ""
    grammar: TutorGrammarSurface | None = None
    session: TutorSessionAwareness = field(default_factory=TutorSessionAwareness)
    adaptive: TutorAdaptiveSurface = field(default_factory=TutorAdaptiveSurface)
    memory: TutorMemorySummary = field(default_factory=TutorMemorySummary)
    teacher_persona: TeacherPersona = field(default_factory=TeacherPersona)
    explanation_style: ExplanationStyle = ExplanationStyle.guided
    explainability_note: str = ""
    safety_code: TutorSafetyCode = TutorSafetyCode.ok
    safety_message: str = ""
    schema_version: int = AI_TUTOR_SCHEMA_VERSION

    def to_prompt_dict(self) -> dict:
        """Opaque dict for LLM — no ORM / engine model leakage."""
        g = self.grammar
        return {
            "student_id": self.student_id,
            "language_id": self.language_id,
            "as_of": self.as_of,
            "student_language": self.student_language,
            "curriculum_version": self.curriculum_version,
            "grammar": (
                {
                    "grammar_id": g.grammar_id,
                    "display_code": g.display_code,
                    "display_name": g.display_name,
                    "cefr_band": g.cefr_band,
                    "teaching_notes": g.teaching_notes,
                    "examples": list(g.examples),
                    "common_mistakes": list(g.common_mistakes),
                    "learning_objectives": list(g.learning_objectives),
                }
                if g
                else None
            ),
            "session": {
                "lesson_id": self.session.lesson_id,
                "lesson_objective": self.session.lesson_objective,
                "grammar_id": self.session.grammar_id,
                "current_activity_id": self.session.current_activity_id,
                "current_step_id": self.session.current_step_id,
                "completed_activity_ids": list(self.session.completed_activity_ids),
                "remaining_activity_ids": list(self.session.remaining_activity_ids),
                "runtime_state": self.session.runtime_state,
            },
            "adaptive": {
                "preferred_pace": self.adaptive.preferred_pace,
                "preferred_explanation_depth": self.adaptive.preferred_explanation_depth,
                "preferred_examples": self.adaptive.preferred_examples,
                "average_confidence": self.adaptive.average_confidence,
                "difficulty_level": self.adaptive.difficulty_level,
                "learning_confidence_current": self.adaptive.learning_confidence_current,
                "mastery_score_current": self.adaptive.mastery_score_current,
                "weak_grammar_ids": list(self.adaptive.weak_grammar_ids),
                "review_horizons": list(self.adaptive.review_horizons),
                "weakness_signal_kinds": list(self.adaptive.weakness_signal_kinds),
                "remediation_kinds": list(self.adaptive.remediation_kinds),
                "activity_mix": dict(self.adaptive.activity_mix),
                "explainability_notes": list(self.adaptive.explainability_notes),
            },
            "memory": {
                "preferred_tone": self.memory.preferred_tone,
                "preferred_examples": self.memory.preferred_examples,
                "explanation_preference": self.memory.explanation_preference,
                "recurring_questions": list(self.memory.recurring_questions),
                "unfinished_discussion": self.memory.unfinished_discussion,
                "recent_turn_summaries": list(self.memory.recent_turn_summaries),
            },
            "teacher_persona": {
                "persona_id": self.teacher_persona.persona_id,
                "tone": self.teacher_persona.tone,
                "extras": dict(self.teacher_persona.extras),
            },
            "explanation_style": self.explanation_style.value,
            "explainability_note": self.explainability_note,
            "safety_code": self.safety_code.value,
        }


@dataclass(frozen=True, slots=True)
class ConversationTurn:
    role: str  # student | tutor
    content: str
    prompt_kind: str = ""
    created_at: str = ""


@dataclass(frozen=True, slots=True)
class ConversationMemory:
    """Dedicated tutor conversation memory — separated from educational state."""

    student_id: int
    language_id: int
    conversation_id: str
    preferred_tone: str = "supportive"
    explanation_preference: str = "guided"
    preferred_examples: str = "everyday"
    recurring_questions: tuple[str, ...] = ()
    unfinished_discussion: str = ""
    turns: tuple[ConversationTurn, ...] = ()
    schema_version: int = AI_TUTOR_SCHEMA_VERSION
    updated_at: str = ""


@dataclass(frozen=True, slots=True)
class TutorPromptBundle:
    system: str
    user: str
    prompt_kind: TutorPromptKind
    template_version: str = "e1.0.0"


@dataclass(frozen=True, slots=True)
class TutorResponse:
    utterance: str
    prompt_kind: TutorPromptKind
    grammar_id: str | None
    explanation_style: ExplanationStyle
    explainability_note: str
    safety_code: TutorSafetyCode
    provider: str
    conversation_id: str
    context_as_of: str
    schema_version: int = AI_TUTOR_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class TutorTurnRequest:
    """Inbound student message + optional session anchors (fail-closed if grammar missing)."""

    student_id: int
    language_id: int = 1
    message: str = ""
    prompt_kind: TutorPromptKind = TutorPromptKind.answer_question
    conversation_id: str | None = None
    grammar_id: str | None = None
    lesson_id: str | None = None
    activity_id: str | None = None
    step_id: str | None = None
    student_language: str = "en"
    teacher_persona: TeacherPersona | None = None
    as_of: str | None = None
