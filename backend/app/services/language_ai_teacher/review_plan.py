"""Review planner — deterministic; never unlocks grammar."""

from __future__ import annotations

from app.services.language_adaptive_intelligence.enums import ReviewHorizon
from app.services.language_adaptive_intelligence.types import AdaptiveIntelligenceBundle
from app.services.language_ai_teacher.enums import ReviewPlanKind
from app.services.language_ai_teacher.types import ExplainableNote, ReviewPlan
from app.services.language_grammar_catalog.catalog import get_topic


def plan_review(adaptive: AdaptiveIntelligenceBundle | None) -> ReviewPlan:
    if adaptive is None or not adaptive.enabled:
        return ReviewPlan(
            kind=ReviewPlanKind.none,
            minutes=0,
            reasons=(
                ExplainableNote(
                    code="no_adaptive",
                    message="No adaptive signals available — skip dedicated review block.",
                ),
            ),
        )

    recs = list(adaptive.review_recommendations)
    if not recs:
        conf = adaptive.profile.average_confidence
        if conf >= 70.0:
            return ReviewPlan(
                kind=ReviewPlanKind.none,
                minutes=0,
                reasons=(
                    ExplainableNote(
                        code="high_confidence",
                        message=f"Average confidence {conf:.0f}% with empty review queue — no review needed.",
                    ),
                ),
            )
        return ReviewPlan(
            kind=ReviewPlanKind.minutes_5,
            minutes=5,
            reasons=(
                ExplainableNote(
                    code="soft_confidence",
                    message=f"Confidence {conf:.0f}% — light 5-minute warm-up review.",
                ),
            ),
        )

    top = recs[0]
    topic = get_topic(top.grammar_id)
    name = topic.display_name if topic else top.display_name or top.grammar_id
    reasons = [
        ExplainableNote(code="adaptive_review", message=r.message)
        for r in top.reasons[:3]
    ] or [
        ExplainableNote(
            code="top_urgency",
            message=f"Highest urgency review item is {name} (urgency {top.urgency:.0f}).",
        )
    ]

    if top.horizon is ReviewHorizon.today or top.urgency >= 70.0:
        kind = ReviewPlanKind.minutes_10
        minutes = 10
        if "vocabulary" in " ".join(r.message.lower() for r in top.reasons):
            kind = ReviewPlanKind.vocabulary_recap
        elif any("retention" in r.message.lower() or "confidence" in r.message.lower() for r in top.reasons):
            kind = ReviewPlanKind.grammar_recap
    elif top.horizon is ReviewHorizon.tomorrow or top.urgency >= 45.0:
        kind = ReviewPlanKind.minutes_5
        minutes = 5
    else:
        # this week / later — short grammar recap only if retention risk signals present
        signals = {s.kind.value for s in adaptive.signals}
        if "retention_risk" in signals or "forgotten_grammar" in signals:
            kind = ReviewPlanKind.grammar_recap
            minutes = 5
        elif "skill_gap" in signals:
            kind = ReviewPlanKind.reading_recap
            minutes = 5
        else:
            kind = ReviewPlanKind.none
            minutes = 0

    return ReviewPlan(
        kind=kind,
        minutes=minutes,
        focus_grammar_id=top.grammar_id,
        focus_display_name=name,
        reasons=tuple(reasons),
    )
