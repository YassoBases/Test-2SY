"""Autonomous AI Teacher contracts (Phase F).

Orchestrates HOW today's learning session is conducted.
Never owns grammar progression, mastery, unlocks, or curriculum.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.services.language_ai_teacher.enums import (
    EnergyLevel,
    ReviewPlanKind,
    SessionSectionKind,
    Weekday,
)

AI_TEACHER_SCHEMA_VERSION = 1
AI_TEACHER_JSONB_NAMESPACE = "ai_teacher"
AI_TEACHER_PACKAGE = "language_ai_teacher"


@dataclass(frozen=True, slots=True)
class ExplainableNote:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class DailyGoal:
    goal_id: str
    title: str
    source: str  # grammar | adaptive | review | skill
    grammar_id: str | None = None
    skill: str | None = None
    reasons: tuple[ExplainableNote, ...] = ()


@dataclass(frozen=True, slots=True)
class ReviewPlan:
    kind: ReviewPlanKind
    minutes: int
    focus_grammar_id: str | None = None
    focus_display_name: str = ""
    reasons: tuple[ExplainableNote, ...] = ()


@dataclass(frozen=True, slots=True)
class SessionActivity:
    activity_id: str
    kind: str  # reading | listening | speaking | writing | vocabulary | quiz | grammar
    title: str
    purpose: str
    estimated_minutes: int = 5
    grammar_id: str | None = None


@dataclass(frozen=True, slots=True)
class SessionSection:
    kind: SessionSectionKind
    title: str
    purpose: str
    estimated_minutes: int = 3
    activities: tuple[SessionActivity, ...] = ()


@dataclass(frozen=True, slots=True)
class LearningMission:
    mission_id: str
    title: str
    scenario: str
    grammar_id: str
    grammar_display_name: str
    reasons: tuple[ExplainableNote, ...] = ()


@dataclass(frozen=True, slots=True)
class EnergyAssessment:
    level: EnergyLevel
    score: float  # 0–100
    recommendations: tuple[str, ...] = ()
    reasons: tuple[ExplainableNote, ...] = ()


@dataclass(frozen=True, slots=True)
class WeeklyDayPlan:
    day: Weekday
    focus: str
    activity_kinds: tuple[str, ...] = ()
    notes: str = ""


@dataclass(frozen=True, slots=True)
class WeeklyPlan:
    student_id: int
    language_id: int
    days: tuple[WeeklyDayPlan, ...]
    reasons: tuple[ExplainableNote, ...] = ()
    as_of: str = ""


@dataclass(frozen=True, slots=True)
class LearningJourney:
    """Read-only journey projection — never mutates educational state."""

    current_mission: str = ""
    todays_progress_percent: float = 0.0
    grammar_completed_count: int = 0
    grammar_total_count: int = 0
    current_grammar_id: str | None = None
    current_grammar_name: str = ""
    confidence_trend: str = "steady"  # rising | steady | soft
    weekly_streak_days: int = 0
    upcoming_lesson: str = ""
    reasons: tuple[ExplainableNote, ...] = ()


@dataclass(frozen=True, slots=True)
class SessionWrapUp:
    achievements: tuple[str, ...] = ()
    strongest_skill_today: str = ""
    most_difficult_concept: str = ""
    recommendation: str = ""
    tomorrow_focus: str = ""
    encouragement: str = ""
    reasons: tuple[ExplainableNote, ...] = ()


@dataclass(frozen=True, slots=True)
class LearningSession:
    """Complete AI Teacher session plan for one learning start."""

    session_id: str
    student_id: int
    language_id: int
    as_of: str
    curriculum_version: str
    current_grammar_id: str | None
    current_grammar_name: str
    goals: tuple[DailyGoal, ...]
    review: ReviewPlan
    mission: LearningMission | None
    sections: tuple[SessionSection, ...]
    activity_order: tuple[str, ...]  # activity kinds in teaching order
    energy: EnergyAssessment
    weekly: WeeklyPlan | None = None
    journey: LearningJourney = field(default_factory=LearningJourney)
    wrap_up_preview: SessionWrapUp | None = None
    explanation_strategy: str = "guided"
    pacing: str = "steady"
    schema_version: int = AI_TEACHER_SCHEMA_VERSION

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "student_id": self.student_id,
            "language_id": self.language_id,
            "as_of": self.as_of,
            "curriculum_version": self.curriculum_version,
            "current_grammar_id": self.current_grammar_id,
            "current_grammar_name": self.current_grammar_name,
            "goals": [
                {
                    "goal_id": g.goal_id,
                    "title": g.title,
                    "source": g.source,
                    "grammar_id": g.grammar_id,
                    "skill": g.skill,
                    "reasons": [r.message for r in g.reasons],
                }
                for g in self.goals
            ],
            "review": {
                "kind": self.review.kind.value,
                "minutes": self.review.minutes,
                "focus_grammar_id": self.review.focus_grammar_id,
                "focus_display_name": self.review.focus_display_name,
                "reasons": [r.message for r in self.review.reasons],
            },
            "mission": (
                {
                    "mission_id": self.mission.mission_id,
                    "title": self.mission.title,
                    "scenario": self.mission.scenario,
                    "grammar_id": self.mission.grammar_id,
                    "grammar_display_name": self.mission.grammar_display_name,
                    "reasons": [r.message for r in self.mission.reasons],
                }
                if self.mission
                else None
            ),
            "sections": [
                {
                    "kind": s.kind.value,
                    "title": s.title,
                    "purpose": s.purpose,
                    "estimated_minutes": s.estimated_minutes,
                    "activities": [
                        {
                            "activity_id": a.activity_id,
                            "kind": a.kind,
                            "title": a.title,
                            "purpose": a.purpose,
                            "estimated_minutes": a.estimated_minutes,
                            "grammar_id": a.grammar_id,
                        }
                        for a in s.activities
                    ],
                }
                for s in self.sections
            ],
            "activity_order": list(self.activity_order),
            "energy": {
                "level": self.energy.level.value,
                "score": self.energy.score,
                "recommendations": list(self.energy.recommendations),
                "reasons": [r.message for r in self.energy.reasons],
            },
            "weekly": (
                {
                    "days": [
                        {
                            "day": d.day.value,
                            "focus": d.focus,
                            "activity_kinds": list(d.activity_kinds),
                            "notes": d.notes,
                        }
                        for d in self.weekly.days
                    ],
                    "reasons": [r.message for r in self.weekly.reasons],
                }
                if self.weekly
                else None
            ),
            "journey": {
                "current_mission": self.journey.current_mission,
                "todays_progress_percent": self.journey.todays_progress_percent,
                "grammar_completed_count": self.journey.grammar_completed_count,
                "grammar_total_count": self.journey.grammar_total_count,
                "current_grammar_id": self.journey.current_grammar_id,
                "current_grammar_name": self.journey.current_grammar_name,
                "confidence_trend": self.journey.confidence_trend,
                "weekly_streak_days": self.journey.weekly_streak_days,
                "upcoming_lesson": self.journey.upcoming_lesson,
            },
            "wrap_up_preview": (
                {
                    "achievements": list(self.wrap_up_preview.achievements),
                    "strongest_skill_today": self.wrap_up_preview.strongest_skill_today,
                    "most_difficult_concept": self.wrap_up_preview.most_difficult_concept,
                    "recommendation": self.wrap_up_preview.recommendation,
                    "tomorrow_focus": self.wrap_up_preview.tomorrow_focus,
                    "encouragement": self.wrap_up_preview.encouragement,
                    "reasons": [r.message for r in self.wrap_up_preview.reasons],
                }
                if self.wrap_up_preview
                else None
            ),
            "explanation_strategy": self.explanation_strategy,
            "pacing": self.pacing,
            "schema_version": self.schema_version,
        }
