"""AI Tutor Foundation enums — communication modes only; never educational state."""

from __future__ import annotations

from enum import StrEnum


class TutorPromptKind(StrEnum):
    """Modular prompt templates for Wave E1 (+ future E2 modes)."""

    explain = "explain"
    hint = "hint"
    quiz_help = "quiz_help"
    review = "review"
    motivation = "motivation"
    lesson_summary = "lesson_summary"
    answer_question = "answer_question"


class TutorSafetyCode(StrEnum):
    ok = "ok"
    no_grammar = "no_grammar"
    grammar_mismatch = "grammar_mismatch"
    curriculum_contradiction = "curriculum_contradiction"
    disabled = "disabled"


class ExplanationStyle(StrEnum):
    simplified = "simplified"
    guided = "guided"
    concise = "concise"
    analogy = "analogy"
