"""Energy awareness — recommend lighter pacing; never auto-end lessons."""

from __future__ import annotations

from app.services.language_adaptive_intelligence.types import AdaptiveIntelligenceBundle
from app.services.language_ai_teacher.enums import EnergyLevel
from app.services.language_ai_teacher.types import EnergyAssessment, ExplainableNote


def assess_energy(
    *,
    adaptive: AdaptiveIntelligenceBundle | None,
    coaching_mistake_count: int = 0,
    session_length_minutes: int = 0,
    response_slow: bool = False,
) -> EnergyAssessment:
    score = 70.0
    reasons: list[ExplainableNote] = []

    if adaptive and adaptive.enabled:
        conf = adaptive.profile.average_confidence
        score = 0.5 * score + 0.5 * conf
        reasons.append(
            ExplainableNote(
                code="confidence",
                message=f"Average learning confidence is {conf:.0f}%.",
            )
        )
        if adaptive.profile.retry_frequency >= 0.5:
            score -= 15.0
            reasons.append(
                ExplainableNote(
                    code="retries",
                    message="Elevated retry frequency suggests mental load.",
                )
            )

    if coaching_mistake_count >= 3:
        score -= 12.0
        reasons.append(
            ExplainableNote(
                code="mistakes",
                message=f"{coaching_mistake_count} recent coaching mistakes — energy may be dipping.",
            )
        )
    if session_length_minutes >= 35:
        score -= 10.0
        reasons.append(
            ExplainableNote(
                code="session_length",
                message=f"Session already ~{session_length_minutes} minutes — suggest lighter steps.",
            )
        )
    if response_slow:
        score -= 8.0
        reasons.append(
            ExplainableNote(
                code="response_speed",
                message="Slower responses observed — recommend shorter explanations.",
            )
        )

    score = max(0.0, min(100.0, round(score, 2)))
    if score < 40.0:
        level = EnergyLevel.low
        recs = (
            "Use shorter explanations",
            "Suggest a short break",
            "Switch to a lighter activity",
        )
    elif score >= 70.0:
        level = EnergyLevel.high
        recs = ("Keep a steady challenge pace",)
    else:
        level = EnergyLevel.steady
        recs = ("Keep guided pacing",)

    if not reasons:
        reasons.append(
            ExplainableNote(code="default_energy", message="Using baseline steady energy estimate.")
        )

    return EnergyAssessment(
        level=level,
        score=score,
        recommendations=recs,
        reasons=tuple(reasons),
    )
