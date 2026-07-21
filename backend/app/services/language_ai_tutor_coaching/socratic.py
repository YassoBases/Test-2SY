"""Socratic tutoring — guide first; reveal only when appropriate."""

from __future__ import annotations

from app.services.language_ai_tutor.types import TutorContext
from app.services.language_ai_tutor_coaching.enums import HintLevel
from app.services.language_ai_tutor_coaching.types import HintStep


SOCRATIC_BANK: tuple[str, ...] = (
    "What do you notice about the verb?",
    "What tense is the sentence describing?",
    "What happened first?",
    "Which word signals the time meaning?",
    "If you change the subject, what must stay the same?",
)


def opening_socratic_question(ctx: TutorContext, *, hint_index: int = 0) -> str:
    g = ctx.grammar
    name = g.display_name if g else "this structure"
    if hint_index <= 0:
        return f"Before we settle on an answer for {name}: what do you notice about the verb?"
    if hint_index == 1:
        return "What tense is the sentence describing?"
    if hint_index == 2:
        return "What happened first in the situation?"
    return SOCRATIC_BANK[hint_index % len(SOCRATIC_BANK)]


def compose_guided_utterance(
    *,
    lead: str,
    hint: HintStep | None,
    prefer_question_first: bool,
) -> str:
    """Prefer guiding questions before answers."""
    if hint is None:
        return lead.strip()
    if prefer_question_first and hint.level in {
        HintLevel.level_1,
        HintLevel.level_2,
        HintLevel.level_3,
    }:
        parts = [hint.socratic_question, hint.text]
        if lead:
            parts.append(lead)
        return " ".join(p for p in parts if p).strip()
    parts = [hint.text]
    if hint.socratic_question:
        parts.append(hint.socratic_question)
    if lead:
        parts.append(lead)
    return " ".join(p for p in parts if p).strip()


def avoids_immediate_answer(utterance: str) -> bool:
    """Heuristic used by verification — coaching should not lead with the answer."""
    lowered = utterance.strip().lower()
    banned_prefixes = (
        "the answer is",
        "correct answer:",
        "answer:",
        "it's simply",
        "it is simply",
    )
    return not any(lowered.startswith(p) for p in banned_prefixes)
