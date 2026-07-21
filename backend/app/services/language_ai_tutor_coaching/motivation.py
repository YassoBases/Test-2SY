"""Motivation strategy — authentic encouragement; avoid exaggerated praise."""

from __future__ import annotations

from app.services.language_ai_tutor.types import TutorContext
from app.services.language_ai_tutor_coaching.types import CoachingSessionState


def motivation_line(
    ctx: TutorContext,
    state: CoachingSessionState,
    *,
    just_improved: bool = False,
    after_mistake: bool = False,
    low_confidence: bool = False,
) -> str:
    """Short, authentic encouragement — never over-the-top."""
    if after_mistake:
        return "Mistakes are useful here — they show exactly what to tighten next."
    if just_improved:
        return "Nice progress — your reasoning is getting clearer."
    if low_confidence:
        return "Take this one step at a time; small checks build steady confidence."
    if state.encouragement_count == 0:
        return "Good effort staying with the pattern — keep going."
    # Rotate lightly to avoid identical praise spam
    options = (
        "Solid focus on the grammar target.",
        "You're putting in real work — that compounds.",
        "Keep testing the rule in a new sentence when you're ready.",
    )
    return options[state.encouragement_count % len(options)]


def praise_is_appropriate(line: str) -> bool:
    """Verification helper — reject exaggerated praise."""
    banned = ("genius", "perfect forever", "best student ever", "amazing!!!!", "incredible!!!")
    lowered = line.lower()
    return not any(b in lowered for b in banned) and line.count("!") <= 1
