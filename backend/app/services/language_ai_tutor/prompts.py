"""Prompt Orchestrator — modular templates; never raw DB models."""

from __future__ import annotations

import json

from app.services.language_ai_tutor.enums import TutorPromptKind
from app.services.language_ai_tutor.explanation import style_instruction
from app.services.language_ai_tutor.persona import persona_system_lines
from app.services.language_ai_tutor.types import TutorContext, TutorPromptBundle

TEMPLATE_VERSION = "e1.0.0"

_KIND_INSTRUCTIONS: dict[TutorPromptKind, str] = {
    TutorPromptKind.explain: (
        "Explain the current grammar concept clearly for this lesson. "
        "Do not introduce a different grammar topic."
    ),
    TutorPromptKind.hint: (
        "Give a short hint that helps the student progress on the current activity "
        "without revealing a full answer dump."
    ),
    TutorPromptKind.quiz_help: (
        "Help the student reason about the current quiz/activity item. "
        "Guide; do not invent new curriculum."
    ),
    TutorPromptKind.review: (
        "Provide a brief review of the current grammar focus using prior practice signals. "
        "Recommend practice only; never unlock grammar."
    ),
    TutorPromptKind.motivation: (
        "Motivate the student briefly and specifically about the current lesson focus."
    ),
    TutorPromptKind.lesson_summary: (
        "Summarize what the student is working on in this lesson session "
        "(objective, current activity, remaining work). Do not invent progression."
    ),
    TutorPromptKind.answer_question: (
        "Answer the student's question about the current grammar/lesson only."
    ),
}


def _shared_system(ctx: TutorContext) -> str:
    lines = [
        "You are the EduSpark AI Tutor Foundation (Wave E1).",
        "You communicate educational decisions that already exist — you are NOT a learning engine.",
        "Hard rules:",
        "- ONLY discuss the grammar_id in tutor_context.grammar.",
        "- NEVER choose, unlock, or change grammar targets.",
        "- NEVER invent mastery, progression, evidence, or curriculum.",
        "- NEVER claim the student completed or unlocked topics.",
        "- If asked about a different grammar than today's focus, redirect to current grammar.",
        "- Keep replies short (2–6 sentences) unless summarizing a lesson.",
        "- Be transparent when simplifying: you may mention the explainability_note.",
    ]
    lines.extend(persona_system_lines(ctx.teacher_persona))
    lines.append(f"Explanation style: {ctx.explanation_style.value}.")
    lines.append(style_instruction(ctx.explanation_style))
    if ctx.explainability_note:
        lines.append(f"Explainability: {ctx.explainability_note}")
    lines.append(
        'Respond with JSON only: {"utterance":"...","meta":{"stayed_on_grammar":true}}'
    )
    return "\n".join(lines)


def build_prompt_bundle(
    ctx: TutorContext,
    *,
    prompt_kind: TutorPromptKind,
    student_message: str = "",
) -> TutorPromptBundle:
    """Tutor Context → modular LLM prompt (no engine models)."""
    kind = prompt_kind if prompt_kind in _KIND_INSTRUCTIONS else TutorPromptKind.answer_question
    payload = {
        "mode": kind.value,
        "mode_instruction": _KIND_INSTRUCTIONS[kind],
        "student_message": student_message.strip(),
        "tutor_context": ctx.to_prompt_dict(),
    }
    user = (
        "Use ONLY the following tutor_context projection. "
        "Do not assume database fields beyond this JSON.\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
    )
    return TutorPromptBundle(
        system=_shared_system(ctx),
        user=user,
        prompt_kind=kind,
        template_version=TEMPLATE_VERSION,
    )


def template_fallback_utterance(
    ctx: TutorContext,
    *,
    prompt_kind: TutorPromptKind,
    student_message: str = "",
) -> str:
    """Deterministic fallback when Claude is unavailable — still safety-bound."""
    g = ctx.grammar
    name = g.display_name if g else "this lesson"
    gid = g.grammar_id if g else "unknown"
    style_note = ctx.explainability_note or "I'll keep this clear and supportive."
    base = {
        TutorPromptKind.explain: (
            f"Today we are focusing on {name} ({gid}). "
            f"{(g.teaching_notes if g and g.teaching_notes else 'Let us look at the core pattern together.')} "
            f"{style_note}"
        ),
        TutorPromptKind.hint: (
            f"Hint for {name}: look at the pattern in your current activity, "
            f"then try one short example using that structure. {style_note}"
        ),
        TutorPromptKind.quiz_help: (
            f"For this activity on {name}, check which option matches the grammar pattern "
            f"we are practicing — not a different tense. {style_note}"
        ),
        TutorPromptKind.review: (
            f"Quick review: {name} is your current focus. "
            f"A short practice today will help confidence. {style_note}"
        ),
        TutorPromptKind.motivation: (
            f"You're working on {name} — steady practice builds confidence. "
            f"Let's take the next activity one step at a time."
        ),
        TutorPromptKind.lesson_summary: (
            f"Lesson focus: {name}. "
            f"Current activity: {ctx.session.current_activity_id or ctx.session.current_step_id or 'in progress'}. "
            f"Completed: {len(ctx.session.completed_activity_ids)}; "
            f"remaining: {len(ctx.session.remaining_activity_ids)}. {style_note}"
        ),
        TutorPromptKind.answer_question: (
            f"About {name}: I can help with this lesson's grammar only. "
            f"{('You asked: ' + student_message.strip()[:160]) if student_message.strip() else ''} "
            f"{style_note}"
        ),
    }
    return base.get(prompt_kind, base[TutorPromptKind.answer_question]).strip()
