"""Parent insight projections — simple advisory language only."""

from __future__ import annotations

from app.services.language_adaptive_intelligence.enums import ReviewHorizon
from app.services.language_adaptive_intelligence.types import (
    ExplainableReason,
    ParentInsight,
    ReviewRecommendation,
)
from app.services.language_grammar_catalog.catalog import get_default_catalog, get_topic
from app.services.language_grammar.enums import GrammarMasteryState
from app.services.language_grammar_mastery.types import GrammarMasterySnapshot
from app.services.language_grammar_progression.types import GrammarProgressionSnapshot


def build_parent_insight(
    *,
    mastery: GrammarMasterySnapshot,
    progression: GrammarProgressionSnapshot | None,
    review_recommendations: tuple[ReviewRecommendation, ...],
) -> ParentInsight:
    """Produce a short parent-friendly summary — never unlocks grammar."""
    catalog = get_default_catalog()
    total = max(1, len(catalog.topics))
    mastered = sum(1 for r in mastery.records if r.state is GrammarMasteryState.mastered)
    # Also count high overall as partial progress for friendlier % 
    strong = sum(1 for r in mastery.records if float(r.dimensions.overall_mastery) >= 80.0)
    percent = round(100.0 * max(mastered, strong) / total, 1)

    cefr = ""
    if progression is not None:
        cefr = progression.anchor_cefr.value if hasattr(progression.anchor_cefr, "value") else str(progression.anchor_cefr)

    focus_id = progression.current_grammar_id if progression else None
    focus_name = "Getting started"
    if focus_id:
        topic = get_topic(focus_id)
        focus_name = topic.display_name if topic else focus_id

    minutes = 15
    text = f"Recommended: {minutes}-minute review this week."
    for rec in review_recommendations:
        if rec.horizon is ReviewHorizon.today:
            minutes = 20
            text = f"Recommended: {minutes}-minute review today focusing on {rec.display_name}."
            break
        if rec.horizon is ReviewHorizon.tomorrow:
            minutes = 15
            text = f"Recommended: {minutes}-minute review tomorrow focusing on {rec.display_name}."
            break
        if rec.horizon is ReviewHorizon.this_week:
            minutes = 15
            text = f"Recommended: {minutes}-minute review this week focusing on {rec.display_name}."
            break

    explanations = (
        ExplainableReason(
            code="mastered_percent",
            message=f"Mastered or strong on {max(mastered, strong)} of {total} catalog topics ({percent}%).",
        ),
        ExplainableReason(
            code="current_focus",
            message=f"Current focus is {focus_name}.",
        ),
        ExplainableReason(
            code="review_advice",
            message=text,
        ),
    )

    return ParentInsight(
        mastered_percent_band=percent,
        cefr_band=cefr,
        current_focus=focus_name,
        current_focus_grammar_id=focus_id,
        recommended_minutes=minutes,
        recommendation_text=text,
        explanations=explanations,
    )


def parent_insight_to_dict(insight: ParentInsight) -> dict:
    return {
        "mastered_percent": insight.mastered_percent_band,
        "cefr_band": insight.cefr_band,
        "current_focus": insight.current_focus,
        "current_focus_grammar_id": insight.current_focus_grammar_id,
        "recommended_minutes": insight.recommended_minutes,
        "recommendation_text": insight.recommendation_text,
        "summary": (
            f"Your child has mastered {insight.mastered_percent_band:.0f}% of "
            f"{insight.cefr_band or 'current'} grammar. "
            f"Current focus: {insight.current_focus}. "
            f"{insight.recommendation_text}"
        ),
        "explanations": [r.message for r in insight.explanations],
        "advisory_only": True,
    }
