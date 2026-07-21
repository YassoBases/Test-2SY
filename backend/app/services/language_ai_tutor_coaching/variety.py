"""Explanation variety — choose style from Learning Profile / E1 explanation style."""

from __future__ import annotations

from app.services.language_ai_tutor.enums import ExplanationStyle
from app.services.language_ai_tutor.types import TutorContext
from app.services.language_ai_tutor_coaching.enums import ExplanationVariety


def choose_explanation_variety(ctx: TutorContext) -> ExplanationVariety:
    """Map locked E1 explanation style + adaptive signals → variety."""
    style = ctx.explanation_style
    signals = set(ctx.adaptive.weakness_signal_kinds)

    if "recurring_mistakes" in signals or style is ExplanationStyle.analogy:
        return ExplanationVariety.analogy
    if style is ExplanationStyle.simplified:
        return ExplanationVariety.example_based
    if style is ExplanationStyle.concise:
        return ExplanationVariety.rule_based
    if ctx.adaptive.preferred_examples in {"everyday", "workplace"}:
        return ExplanationVariety.visual_imagination
    return ExplanationVariety.step_by_step


def variety_instruction(variety: ExplanationVariety) -> str:
    return {
        ExplanationVariety.rule_based: "Lead with a short clear rule, then one tight example.",
        ExplanationVariety.example_based: "Lead with examples before naming the rule.",
        ExplanationVariety.analogy: "Use a simple everyday analogy, then connect it to the grammar.",
        ExplanationVariety.visual_imagination: (
            "Help the student picture the timeline or situation before the form."
        ),
        ExplanationVariety.step_by_step: "Use numbered reasoning steps; one idea per step.",
    }[variety]
