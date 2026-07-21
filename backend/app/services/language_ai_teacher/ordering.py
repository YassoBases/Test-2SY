"""Dynamic activity ordering — never changes lesson objectives / grammar targets."""

from __future__ import annotations

from app.services.language_adaptive_intelligence.types import AdaptiveIntelligenceBundle
from app.services.language_ai_teacher.enums import EnergyLevel
from app.services.language_ai_teacher.types import ExplainableNote, SessionActivity

DEFAULT_ORDER: tuple[str, ...] = (
    "grammar",
    "reading",
    "listening",
    "speaking",
    "writing",
    "vocabulary",
    "quiz",
)


def order_activity_kinds(
    adaptive: AdaptiveIntelligenceBundle | None,
    *,
    energy: EnergyLevel = EnergyLevel.steady,
) -> tuple[tuple[str, ...], tuple[ExplainableNote, ...]]:
    """Return ordered activity kinds + explainability notes."""
    order = list(DEFAULT_ORDER)
    reasons: list[ExplainableNote] = []

    if adaptive and adaptive.enabled:
        mix = adaptive.activity_mix.as_dict()
        # Sort practice skills by adaptive weight (desc), keep grammar/quiz anchors
        practice = ["reading", "listening", "speaking", "writing", "vocabulary"]
        practice.sort(key=lambda k: (-float(mix.get(k, 1.0)), k))
        order = ["grammar", *practice, "quiz"]
        top = practice[0]
        if float(mix.get(top, 1.0)) >= 1.2:
            # Move boosted skill earlier (right after grammar)
            reasons.append(
                ExplainableNote(
                    code="boost_skill",
                    message=f"Adaptive mix boosts {top} — schedule it earlier in practice.",
                )
            )
        conf = adaptive.profile.average_confidence
        if conf >= 75.0:
            # Challenge: quiz earlier (after first practice)
            if "quiz" in order:
                order.remove("quiz")
                insert_at = min(2, len(order))
                order.insert(insert_at, "quiz")
            reasons.append(
                ExplainableNote(
                    code="high_confidence",
                    message="High confidence — introduce a challenge quiz earlier.",
                )
            )

    if energy is EnergyLevel.low:
        # Shorter reading: push reading later; prefer speaking/listening lighter slots earlier
        if "reading" in order:
            order.remove("reading")
            order.insert(len(order) - 1, "reading")
        reasons.append(
            ExplainableNote(
                code="low_energy",
                message="Energy is low — shorten reading and keep lighter activities earlier.",
            )
        )

    if not reasons:
        reasons.append(
            ExplainableNote(
                code="default_order",
                message="Using balanced default activity order.",
            )
        )
    return tuple(order), tuple(reasons)


def build_ordered_activities(
    *,
    grammar_id: str | None,
    grammar_name: str,
    kind_order: tuple[str, ...],
    energy: EnergyLevel,
) -> tuple[SessionActivity, ...]:
    minutes = {
        "grammar": 8,
        "reading": 6 if energy is not EnergyLevel.low else 4,
        "listening": 5,
        "speaking": 7,
        "writing": 6,
        "vocabulary": 4,
        "quiz": 5,
    }
    titles = {
        "grammar": f"Main lesson: {grammar_name}",
        "reading": "Reading practice",
        "listening": "Listening practice",
        "speaking": "Speaking practice",
        "writing": "Writing practice",
        "vocabulary": "Vocabulary support",
        "quiz": "Quick check quiz",
    }
    purposes = {
        "grammar": "Teach today's grammar target with guided explanation.",
        "reading": "Reinforce the grammar target through reading.",
        "listening": "Hear the target forms in context.",
        "speaking": "Produce the target forms aloud.",
        "writing": "Write using the target grammar.",
        "vocabulary": "Light lexical support aligned to today's grammar.",
        "quiz": "Check understanding without changing objectives.",
    }
    out: list[SessionActivity] = []
    for kind in kind_order:
        out.append(
            SessionActivity(
                activity_id=f"act_{kind}",
                kind=kind,
                title=titles.get(kind, kind.title()),
                purpose=purposes.get(kind, "Practice today's learning goal."),
                estimated_minutes=minutes.get(kind, 5),
                grammar_id=grammar_id,
            )
        )
    return tuple(out)
