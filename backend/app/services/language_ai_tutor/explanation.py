"""Adaptive explanation style — uses Learning Profile projections only.

Never modifies grammar targets, mastery, or adaptive profile.
"""

from __future__ import annotations

from app.services.language_ai_tutor.enums import ExplanationStyle
from app.services.language_ai_tutor.types import TutorAdaptiveSurface


def decide_explanation_style(adaptive: TutorAdaptiveSurface) -> tuple[ExplanationStyle, str]:
    """Map profile/confidence/signals → explanation style + explainability note."""
    conf = adaptive.learning_confidence_current
    if conf is None:
        conf = adaptive.average_confidence

    signals = set(adaptive.weakness_signal_kinds)
    depth = adaptive.preferred_explanation_depth
    pace = adaptive.preferred_pace

    if "recurring_mistakes" in signals or "unstable_performance" in signals:
        return (
            ExplanationStyle.analogy,
            "This explanation uses an analogy because recent mistakes have been recurring.",
        )

    if conf < 45.0 or pace == "slow" or depth == "detailed":
        return (
            ExplanationStyle.simplified,
            "This explanation is simplified because your recent confidence has been low.",
        )

    if conf >= 75.0 and depth == "brief" and pace == "fast":
        return (
            ExplanationStyle.concise,
            "This explanation is concise because your confidence is high.",
        )

    if "low_confidence" in signals or "retention_risk" in signals:
        return (
            ExplanationStyle.simplified,
            "This explanation adds extra examples because retention confidence is soft.",
        )

    return (
        ExplanationStyle.guided,
        "This explanation uses a guided pace matching your learning profile.",
    )


def style_instruction(style: ExplanationStyle) -> str:
    if style is ExplanationStyle.simplified:
        return (
            "Use simpler wording, more examples, and a slower step-by-step explanation. "
            "Keep vocabulary lighter."
        )
    if style is ExplanationStyle.concise:
        return (
            "Keep the explanation short and precise. Higher vocabulary is acceptable. "
            "Avoid over-scaffolding."
        )
    if style is ExplanationStyle.analogy:
        return (
            "Lead with a clear everyday analogy, then connect it back to the grammar pattern. "
            "Include one corrective example of a common mistake."
        )
    return (
        "Use a clear guided explanation with one short example and one practice nudge. "
        "Stay supportive and patient."
    )
