"""Adaptive Intelligence enums — never alter curriculum or mastery states."""

from __future__ import annotations

from enum import StrEnum


class AdaptiveDifficulty(StrEnum):
    easy = "easy"
    normal = "normal"
    advanced = "advanced"


class ReviewHorizon(StrEnum):
    today = "review_today"
    tomorrow = "review_tomorrow"
    this_week = "review_this_week"
    later = "review_later"


class LearningSignalKind(StrEnum):
    recurring_mistakes = "recurring_mistakes"
    forgotten_grammar = "forgotten_grammar"
    low_confidence = "low_confidence"
    repeated_retries = "repeated_retries"
    long_inactivity = "long_inactivity"
    unstable_performance = "unstable_performance"
    retention_risk = "retention_risk"
    skill_gap = "skill_gap"


class RemediationKind(StrEnum):
    easier_explanation = "easier_explanation"
    additional_examples = "additional_examples"
    mini_lesson = "mini_lesson"
    grammar_recap = "grammar_recap"
    vocabulary_support = "vocabulary_support"


class PreferredPace(StrEnum):
    slow = "slow"
    steady = "steady"
    fast = "fast"


class ExplanationDepth(StrEnum):
    brief = "brief"
    guided = "guided"
    detailed = "detailed"
