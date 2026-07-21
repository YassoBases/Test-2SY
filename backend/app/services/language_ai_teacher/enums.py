"""Autonomous AI Teacher enums (Phase F) — session conduct only."""

from __future__ import annotations

from enum import StrEnum


class SessionSectionKind(StrEnum):
    welcome = "welcome"
    todays_goal = "todays_goal"
    quick_review = "quick_review"
    main_lesson = "main_lesson"
    practice = "practice"
    speaking = "speaking"
    quiz = "quiz"
    reflection = "reflection"
    summary = "summary"
    tomorrow_preview = "tomorrow_preview"


class ReviewPlanKind(StrEnum):
    none = "no_review"
    minutes_5 = "5_minute_review"
    minutes_10 = "10_minute_review"
    grammar_recap = "grammar_recap"
    vocabulary_recap = "vocabulary_recap"
    reading_recap = "reading_recap"


class EnergyLevel(StrEnum):
    high = "high"
    steady = "steady"
    low = "low"


class Weekday(StrEnum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"
