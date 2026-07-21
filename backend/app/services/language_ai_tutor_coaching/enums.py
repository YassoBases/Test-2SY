"""Conversational Coaching enums (Wave E2) — behavior only; never educational state."""

from __future__ import annotations

from enum import StrEnum


class CoachingMove(StrEnum):
    """What the coach chooses to do on this turn."""

    explain = "explain"
    hint = "hint"
    question = "question"
    challenge = "challenge"
    review = "review"
    encourage = "encourage"
    recap = "recap"
    diagnose = "diagnose"
    reflect = "reflect"
    wrap_up = "wrap_up"


class HintLevel(StrEnum):
    level_1 = "hint_level_1"
    level_2 = "hint_level_2"
    level_3 = "hint_level_3"
    full_explanation = "full_explanation"
    worked_example = "worked_example"


class MistakeKind(StrEnum):
    grammar_misconception = "grammar_misconception"
    vocabulary_misunderstanding = "vocabulary_misunderstanding"
    reading_misunderstanding = "reading_misunderstanding"
    careless_mistake = "careless_mistake"
    unknown = "unknown"


class ExplanationVariety(StrEnum):
    rule_based = "rule_based"
    example_based = "example_based"
    analogy = "analogy"
    visual_imagination = "visual_imagination"
    step_by_step = "step_by_step"


class StudentIntent(StrEnum):
    """Lightweight intent from the student message (coaching routing only)."""

    ask_answer = "ask_answer"
    ask_hint = "ask_hint"
    submit_attempt = "submit_attempt"
    ask_why = "ask_why"
    request_full_answer = "request_full_answer"
    request_wrap_up = "request_wrap_up"
    general = "general"
