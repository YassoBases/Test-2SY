"""Session wrap-up — achievements and recommendations; explain every recommendation."""

from __future__ import annotations

from app.services.language_adaptive_intelligence.types import AdaptiveIntelligenceBundle
from app.services.language_ai_teacher.types import (
    DailyGoal,
    ExplainableNote,
    LearningMission,
    ReviewPlan,
    SessionWrapUp,
)
from app.services.language_grammar_catalog.catalog import get_topic
from app.services.language_grammar_progression.types import GrammarProgressionSnapshot


def build_session_wrap_up(
    *,
    progression: GrammarProgressionSnapshot | None,
    adaptive: AdaptiveIntelligenceBundle | None,
    goals: tuple[DailyGoal, ...],
    review: ReviewPlan,
    mission: LearningMission | None,
    activity_order: tuple[str, ...],
) -> SessionWrapUp:
    current_id = progression.current_grammar_id if progression else None
    current_name = ""
    if current_id:
        topic = get_topic(current_id)
        current_name = topic.display_name if topic else current_id

    achievements = [
        f"Focused on {current_name or 'today’s grammar target'}",
    ]
    if mission:
        achievements.append(f"Mission framed: {mission.title}")
    if review.minutes > 0:
        achievements.append(f"Completed a {review.minutes}-minute review block plan")
    if goals:
        achievements.append(f"Set {len(goals)} personalized daily goals")

    # Strongest skill from adaptive mix (highest weight among skills practiced early)
    strongest = "reading"
    if adaptive and adaptive.enabled:
        mix = adaptive.activity_mix.as_dict()
        strongest = max(("reading", "listening", "speaking", "writing"), key=lambda k: mix.get(k, 1.0))

    difficult = current_name or "today's grammar"
    if adaptive and adaptive.profile.weak_grammar_ids:
        wid = adaptive.profile.weak_grammar_ids[0]
        wt = get_topic(wid)
        difficult = wt.display_name if wt else wid

    recommendation = "Keep a short practice on today's grammar tomorrow."
    rec_reasons: list[ExplainableNote] = []
    if adaptive and adaptive.review_recommendations:
        top = adaptive.review_recommendations[0]
        recommendation = (
            f"Review {top.display_name or top.grammar_id} "
            f"({top.horizon.value.replace('_', ' ')}) based on adaptive urgency."
        )
        rec_reasons.append(
            ExplainableNote(
                code="adaptive_review",
                message=f"Top adaptive review urgency is {top.urgency:.0f} for {top.grammar_id}.",
            )
        )
    else:
        rec_reasons.append(
            ExplainableNote(
                code="default_rec",
                message="No urgent adaptive review — recommend light continuity practice.",
            )
        )

    tomorrow = "Continue the current grammar with guided practice."
    if progression and progression.next_grammar_id and adaptive and adaptive.profile.average_confidence >= 75:
        nxt = get_topic(progression.next_grammar_id)
        tomorrow = f"Preview informational focus: {nxt.display_name if nxt else progression.next_grammar_id}."
        rec_reasons.append(
            ExplainableNote(
                code="tomorrow_preview",
                message="High confidence allows an informational preview of the next grammar (no unlock).",
            )
        )
    elif current_name:
        tomorrow = f"Tomorrow's focus: continue {current_name}."

    encouragement = "Steady practice beats perfect days — you showed up for today's plan."

    # Mention first activity in order as engagement signal
    if activity_order:
        rec_reasons.append(
            ExplainableNote(
                code="activity_order",
                message=f"Today's practice opened with {activity_order[0]} by adaptive ordering.",
            )
        )

    return SessionWrapUp(
        achievements=tuple(achievements[:5]),
        strongest_skill_today=strongest,
        most_difficult_concept=difficult,
        recommendation=recommendation,
        tomorrow_focus=tomorrow,
        encouragement=encouragement,
        reasons=tuple(rec_reasons),
    )
