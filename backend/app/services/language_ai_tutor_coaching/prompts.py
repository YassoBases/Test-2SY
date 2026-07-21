"""Coaching prompt additions (Wave E2).

Does NOT modify E1 Prompt Orchestrator — builds a coaching overlay prompt
from TutorContext.to_prompt_dict() + coaching decision/state.
"""

from __future__ import annotations

import json

from app.services.language_ai_tutor.types import TutorContext
from app.services.language_ai_tutor_coaching.enums import CoachingMove, HintLevel
from app.services.language_ai_tutor_coaching.types import (
    CoachingDecision,
    CoachingPromptBundle,
    CoachingSessionState,
)
from app.services.language_ai_tutor_coaching.variety import variety_instruction

TEMPLATE_VERSION = "e2.0.0"


def build_coaching_prompt(
    ctx: TutorContext,
    decision: CoachingDecision,
    state: CoachingSessionState,
    *,
    student_message: str = "",
) -> CoachingPromptBundle:
    system_lines = [
        "You are the EduSpark Conversational Coach (Wave E2).",
        "You extend the AI Tutor Foundation — you are still NOT a learning engine.",
        "Teach by coaching: guide first; do not solve immediately unless move allows reveal.",
        "Hard rules:",
        "- Stay on tutor_context.grammar.grammar_id only.",
        "- Never unlock lessons, update mastery/progression, or change adaptive profile.",
        "- Never fabricate grammar topics.",
        "- Prefer Socratic questions before answers when avoid_immediate_answer is true.",
        "- Do not repeat identical explanations from previous_hints/previous_explanations.",
        "- Keep praise authentic; never exaggerated.",
        f"Coaching move: {decision.move.value}.",
        f"Explanation variety: {decision.explanation_variety.value}.",
        variety_instruction(decision.explanation_variety),
    ]
    if decision.avoid_immediate_answer:
        system_lines.append(
            "Do NOT start with 'The answer is...'. Ask or hint first."
        )
    if decision.hint_level is not None:
        system_lines.append(f"Hint ladder position: {decision.hint_level.value}.")
    if decision.include_reflection:
        system_lines.append("End with one short reflection question.")
    if ctx.explainability_note:
        system_lines.append(f"Explainability: {ctx.explainability_note}")
    system_lines.append(
        'Respond JSON only: {"utterance":"...","reflection_question":null|string,'
        '"motivation_line":null|string}'
    )

    payload = {
        "student_message": student_message,
        "coaching_decision": {
            "move": decision.move.value,
            "hint_level": decision.hint_level.value if decision.hint_level else None,
            "explanation_variety": decision.explanation_variety.value,
            "avoid_immediate_answer": decision.avoid_immediate_answer,
            "include_reflection": decision.include_reflection,
            "include_motivation": decision.include_motivation,
            "reasons": list(decision.reasons),
            "diagnosis": (
                {
                    "kind": decision.diagnosis.kind.value,
                    "why": decision.diagnosis.why,
                }
                if decision.diagnosis
                else None
            ),
        },
        "coaching_state": {
            "hint_level_index": state.hint_level_index,
            "previous_hints": list(state.previous_hints[-6:]),
            "previous_explanations": list(state.previous_explanations[-4:]),
            "previous_mistakes": list(state.previous_mistakes[-4:]),
            "last_move": state.last_move,
        },
        "tutor_context": ctx.to_prompt_dict(),
    }
    return CoachingPromptBundle(
        system="\n".join(system_lines),
        user=json.dumps(payload, ensure_ascii=False, indent=2),
        move=decision.move,
        template_version=TEMPLATE_VERSION,
    )


def template_coaching_utterance(
    ctx: TutorContext,
    decision: CoachingDecision,
    *,
    hint_text: str = "",
    socratic_question: str = "",
    reflection_q: str = "",
    motivation: str = "",
    wrap_summary: str = "",
) -> str:
    """Deterministic fallback — still coaching-shaped."""
    g = ctx.grammar
    name = g.display_name if g else "this lesson"

    if decision.move is CoachingMove.wrap_up:
        return wrap_summary or f"Lesson wrap-up for {name}."

    if decision.move is CoachingMove.question:
        q = socratic_question or "What do you notice about the verb?"
        return f"{q} Take a moment before we look at a fuller hint."

    if decision.move is CoachingMove.hint:
        parts = []
        if decision.avoid_immediate_answer and socratic_question:
            parts.append(socratic_question)
        if hint_text:
            parts.append(hint_text)
        if motivation and decision.include_motivation:
            parts.append(motivation)
        return " ".join(parts).strip()

    if decision.move is CoachingMove.diagnose:
        why = decision.diagnosis.why if decision.diagnosis else "Let's examine the mistake carefully."
        parts = [why]
        if socratic_question:
            parts.append(socratic_question)
        elif hint_text:
            parts.append(hint_text)
        if motivation:
            parts.append(motivation)
        return " ".join(parts).strip()

    if decision.move is CoachingMove.challenge:
        return (
            f"Extension for {name}: can you create one new sentence using the same rule "
            f"with a different subject? {motivation}".strip()
        )

    if decision.move is CoachingMove.encourage:
        return (
            f"{motivation or 'Good effort.'} Let's take a smaller step on {name}: "
            f"{socratic_question or 'What do you notice about the verb?'}"
        )

    if decision.move is CoachingMove.reflect:
        return (
            f"You landed the idea for {name}. "
            f"{reflection_q or 'Why do you think this answer is correct?'}"
        )

    # explain / review / recap
    level = decision.hint_level
    lead = hint_text or f"Here is a guided note on {name}."
    if level in {HintLevel.full_explanation, HintLevel.worked_example}:
        body = lead
    else:
        body = f"{socratic_question} {lead}".strip() if socratic_question else lead
    if reflection_q and decision.include_reflection:
        body = f"{body} {reflection_q}"
    if motivation and decision.include_motivation:
        body = f"{body} {motivation}"
    return body.strip()
