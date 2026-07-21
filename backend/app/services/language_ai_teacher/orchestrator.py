"""Session Orchestrator — assemble today's AI Learning Session (pure)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.services.language_adaptive_intelligence.types import AdaptiveIntelligenceBundle
from app.services.language_ai_teacher.energy import assess_energy
from app.services.language_ai_teacher.enums import ReviewPlanKind, SessionSectionKind
from app.services.language_ai_teacher.goals import generate_daily_goals
from app.services.language_ai_teacher.journey import build_learning_journey
from app.services.language_ai_teacher.missions import mission_for_grammar
from app.services.language_ai_teacher.ordering import build_ordered_activities, order_activity_kinds
from app.services.language_ai_teacher.review_plan import plan_review
from app.services.language_ai_teacher.types import (
    LearningSession,
    SessionSection,
)
from app.services.language_ai_teacher.weekly import generate_weekly_plan
from app.services.language_ai_teacher.wrapup import build_session_wrap_up
from app.services.language_grammar_catalog.catalog import get_default_catalog, get_topic
from app.services.language_grammar_mastery.types import GrammarMasterySnapshot
from app.services.language_grammar_progression.types import GrammarProgressionSnapshot


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_session_id() -> str:
    return f"teach_{uuid.uuid4().hex[:16]}"


def orchestrate_learning_session(
    *,
    student_id: int,
    language_id: int = 1,
    mastery: GrammarMasterySnapshot | None = None,
    progression: GrammarProgressionSnapshot | None = None,
    adaptive: AdaptiveIntelligenceBundle | None = None,
    coaching_mistake_count: int = 0,
    session_length_minutes: int = 0,
    response_slow: bool = False,
    as_of: str | None = None,
    session_id: str | None = None,
) -> LearningSession:
    """Generate a complete dynamic lesson plan from existing educational state."""
    stamp = as_of or _now()
    catalog = get_default_catalog()
    current_id = progression.current_grammar_id if progression else None
    if not current_id and adaptive and adaptive.current_grammar_id:
        current_id = adaptive.current_grammar_id
    topic = get_topic(current_id) if current_id else None
    current_name = topic.display_name if topic else (current_id or "Getting started")

    goals = generate_daily_goals(progression=progression, adaptive=adaptive)
    review = plan_review(adaptive)
    mission = mission_for_grammar(current_id)
    energy = assess_energy(
        adaptive=adaptive,
        coaching_mistake_count=coaching_mistake_count,
        session_length_minutes=session_length_minutes,
        response_slow=response_slow,
    )
    kind_order, _order_notes = order_activity_kinds(adaptive, energy=energy.level)
    activities = build_ordered_activities(
        grammar_id=current_id,
        grammar_name=current_name,
        kind_order=kind_order,
        energy=energy.level,
    )

    # Map activities into session structure sections
    practice_acts = tuple(a for a in activities if a.kind not in {"grammar", "speaking", "quiz"})
    speaking_acts = tuple(a for a in activities if a.kind == "speaking")
    quiz_acts = tuple(a for a in activities if a.kind == "quiz")
    main_acts = tuple(a for a in activities if a.kind == "grammar")

    review_minutes = review.minutes
    include_review = review.kind is not ReviewPlanKind.none and review_minutes > 0

    sections: list[SessionSection] = [
        SessionSection(
            kind=SessionSectionKind.welcome,
            title="Welcome",
            purpose="Greet the student and set a supportive tone for today's session.",
            estimated_minutes=2,
        ),
        SessionSection(
            kind=SessionSectionKind.todays_goal,
            title="Today's Goal",
            purpose="Share personalized goals derived from progression and adaptive signals.",
            estimated_minutes=2,
        ),
    ]
    if include_review:
        sections.append(
            SessionSection(
                kind=SessionSectionKind.quick_review,
                title="Quick Review",
                purpose=f"{review.kind.value.replace('_', ' ')} focused on retention.",
                estimated_minutes=review_minutes,
            )
        )
    sections.extend(
        [
            SessionSection(
                kind=SessionSectionKind.main_lesson,
                title="Main Lesson",
                purpose="Teach the current grammar target without changing curriculum.",
                estimated_minutes=8,
                activities=main_acts,
            ),
            SessionSection(
                kind=SessionSectionKind.practice,
                title="Practice",
                purpose="Reorderable multi-skill practice aligned to today's grammar.",
                estimated_minutes=sum(a.estimated_minutes for a in practice_acts) or 10,
                activities=practice_acts,
            ),
            SessionSection(
                kind=SessionSectionKind.speaking,
                title="Speaking",
                purpose="Produce today's grammar in a short spoken mission.",
                estimated_minutes=7,
                activities=speaking_acts,
            ),
            SessionSection(
                kind=SessionSectionKind.quiz,
                title="Quiz",
                purpose="Quick check for understanding — no mastery writes here.",
                estimated_minutes=5,
                activities=quiz_acts,
            ),
            SessionSection(
                kind=SessionSectionKind.reflection,
                title="Reflection",
                purpose="Strengthen learning with a short reflection prompt.",
                estimated_minutes=3,
            ),
            SessionSection(
                kind=SessionSectionKind.summary,
                title="Summary",
                purpose="Recap achievements and explain recommendations.",
                estimated_minutes=3,
            ),
            SessionSection(
                kind=SessionSectionKind.tomorrow_preview,
                title="Tomorrow Preview",
                purpose="Informational preview only — never unlocks grammar.",
                estimated_minutes=2,
            ),
        ]
    )

    weekly = generate_weekly_plan(
        student_id=student_id,
        language_id=language_id,
        adaptive=adaptive,
        as_of=stamp,
    )
    journey = build_learning_journey(
        mastery=mastery,
        progression=progression,
        adaptive=adaptive,
        mission=mission,
    )
    wrap = build_session_wrap_up(
        progression=progression,
        adaptive=adaptive,
        goals=goals,
        review=review,
        mission=mission,
        activity_order=kind_order,
    )

    pacing = "slow" if energy.level.value == "low" else (
        "fast" if energy.level.value == "high" and adaptive and adaptive.profile.average_confidence >= 75
        else "steady"
    )
    explanation = "simplified" if energy.level.value == "low" else "guided"
    if adaptive and adaptive.enabled:
        explanation = adaptive.profile.preferred_explanation_depth.value

    return LearningSession(
        session_id=session_id or new_session_id(),
        student_id=student_id,
        language_id=language_id,
        as_of=stamp,
        curriculum_version=str(catalog.version),
        current_grammar_id=current_id,
        current_grammar_name=current_name,
        goals=goals,
        review=review,
        mission=mission,
        sections=tuple(sections),
        activity_order=kind_order,
        energy=energy,
        weekly=weekly,
        journey=journey,
        wrap_up_preview=wrap,
        explanation_strategy=explanation,
        pacing=pacing,
    )
