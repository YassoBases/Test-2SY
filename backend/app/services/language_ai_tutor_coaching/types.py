"""Conversational Coaching contracts (Wave E2).

Extends tutoring behavior on top of locked AI Tutor Foundation.
Never writes mastery / progression / adaptive / curriculum.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.services.language_ai_tutor_coaching.enums import (
    CoachingMove,
    ExplanationVariety,
    HintLevel,
    MistakeKind,
    StudentIntent,
)

COACHING_SCHEMA_VERSION = 1
COACHING_JSONB_NAMESPACE = "ai_tutor_coaching"
COACHING_PACKAGE = "language_ai_tutor_coaching"


@dataclass(frozen=True, slots=True)
class MistakeDiagnosis:
    kind: MistakeKind
    why: str
    evidence_notes: tuple[str, ...] = ()
    grammar_id: str = ""


@dataclass(frozen=True, slots=True)
class HintStep:
    level: HintLevel
    text: str
    socratic_question: str = ""


@dataclass(frozen=True, slots=True)
class CoachingSessionState:
    """Persisted coaching progression — separate from E1 conversation memory."""

    student_id: int
    language_id: int
    session_id: str
    grammar_id: str = ""
    activity_id: str = ""
    hint_level_index: int = 0  # 0..4 maps to HintLevel order
    previous_hints: tuple[str, ...] = ()
    previous_explanations: tuple[str, ...] = ()
    previous_mistakes: tuple[str, ...] = ()  # MistakeKind values
    diagnoses: tuple[MistakeDiagnosis, ...] = ()
    reflection_pending: bool = False
    last_move: str = ""
    last_utterance_fingerprint: str = ""
    encouragement_count: int = 0
    schema_version: int = COACHING_SCHEMA_VERSION
    updated_at: str = ""


@dataclass(frozen=True, slots=True)
class CoachingDecision:
    move: CoachingMove
    hint_level: HintLevel | None = None
    explanation_variety: ExplanationVariety = ExplanationVariety.step_by_step
    diagnosis: MistakeDiagnosis | None = None
    intent: StudentIntent = StudentIntent.general
    reasons: tuple[str, ...] = ()
    avoid_immediate_answer: bool = True
    include_reflection: bool = False
    include_motivation: bool = False


@dataclass(frozen=True, slots=True)
class LessonWrapUp:
    todays_grammar: str
    grammar_id: str
    common_mistakes: tuple[str, ...] = ()
    strong_performance: tuple[str, ...] = ()
    suggested_review: str = ""
    next_lesson_preview: str = ""
    summary_text: str = ""


@dataclass(frozen=True, slots=True)
class CoachingTurnRequest:
    student_id: int
    language_id: int = 1
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
    as_of: str | None = None


@dataclass(frozen=True, slots=True)
class CoachingTurnResponse:
    utterance: str
    move: CoachingMove
    hint_level: str | None
    explanation_variety: str
    diagnosis_kind: str | None
    diagnosis_why: str = ""
    reflection_question: str = ""
    motivation_line: str = ""
    explainability_note: str = ""
    reasons: tuple[str, ...] = ()
    session_id: str = ""
    grammar_id: str | None = None
    provider: str = "template_fallback"
    wrap_up: LessonWrapUp | None = None
    safety_code: str = "ok"
    schema_version: int = COACHING_SCHEMA_VERSION

    def to_dict(self) -> dict:
        return {
            "utterance": self.utterance,
            "move": self.move.value,
            "hint_level": self.hint_level,
            "explanation_variety": self.explanation_variety,
            "diagnosis_kind": self.diagnosis_kind,
            "diagnosis_why": self.diagnosis_why,
            "reflection_question": self.reflection_question,
            "motivation_line": self.motivation_line,
            "explainability_note": self.explainability_note,
            "reasons": list(self.reasons),
            "session_id": self.session_id,
            "grammar_id": self.grammar_id,
            "provider": self.provider,
            "wrap_up": (
                {
                    "todays_grammar": self.wrap_up.todays_grammar,
                    "grammar_id": self.wrap_up.grammar_id,
                    "common_mistakes": list(self.wrap_up.common_mistakes),
                    "strong_performance": list(self.wrap_up.strong_performance),
                    "suggested_review": self.wrap_up.suggested_review,
                    "next_lesson_preview": self.wrap_up.next_lesson_preview,
                    "summary_text": self.wrap_up.summary_text,
                }
                if self.wrap_up
                else None
            ),
            "safety_code": self.safety_code,
            "schema_version": self.schema_version,
        }


@dataclass(frozen=True, slots=True)
class CoachingPromptBundle:
    system: str
    user: str
    move: CoachingMove
    template_version: str = "e2.0.0"
