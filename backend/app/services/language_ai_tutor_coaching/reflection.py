"""Reflection engine — post-solution questions that strengthen learning."""

from __future__ import annotations

from app.services.language_ai_tutor.types import TutorContext

REFLECTION_BANK: tuple[str, ...] = (
    "Why do you think this answer is correct?",
    "Would this rule work in another sentence?",
    "What clue in the sentence helped you choose the form?",
    "How would the sentence change if the time meaning changed?",
)


def reflection_question(ctx: TutorContext, *, variant: int = 0) -> str:
    g = ctx.grammar
    name = g.display_name if g else "this grammar"
    base = REFLECTION_BANK[variant % len(REFLECTION_BANK)]
    if variant % 2 == 0:
        return base
    return f"For {name}: {base[0].lower()}{base[1:]}"


def should_request_reflection(
    *,
    just_solved: bool,
    revealed_full_explanation: bool,
    reflection_pending: bool,
) -> bool:
    if reflection_pending:
        return True
    return bool(just_solved or revealed_full_explanation)
