"""Lesson wrap-up — informational summary only; never unlocks or updates mastery."""

from __future__ import annotations

from app.services.language_ai_tutor.types import TutorContext
from app.services.language_ai_tutor_coaching.types import CoachingSessionState, LessonWrapUp
from app.services.language_grammar_catalog.catalog import get_topic


def build_lesson_wrap_up(
    ctx: TutorContext,
    state: CoachingSessionState,
    *,
    next_grammar_id: str | None = None,
) -> LessonWrapUp:
    g = ctx.grammar
    grammar_id = (g.grammar_id if g else state.grammar_id) or ""
    name = g.display_name if g else (get_topic(grammar_id).display_name if grammar_id and get_topic(grammar_id) else "today's grammar")

    common = []
    for kind in state.previous_mistakes[-3:]:
        common.append(kind.replace("_", " "))
    if g and g.common_mistakes and not common:
        common.append(g.common_mistakes[0])

    strengths: list[str] = []
    if state.encouragement_count >= 1:
        strengths.append("stayed engaged with guided practice")
    if len(state.previous_hints) >= 1 and request_improved(state):
        strengths.append("used hints to reason instead of guessing only")
    if not strengths:
        strengths.append("showed up for practice on the target grammar")

    review = "A short review of today's pattern later this week would help retention."
    if ctx.adaptive.review_horizons:
        review = f"Suggested review timing from adaptive advice: {ctx.adaptive.review_horizons[0]}."

    next_preview = "Continue with the next unlocked grammar when your lesson path advances."
    if next_grammar_id:
        nxt = get_topic(next_grammar_id)
        if nxt:
            next_preview = f"Next lesson preview (informational only): {nxt.display_name}."

    summary = (
        f"Today's grammar: {name}. "
        f"Common mistakes: {', '.join(common) if common else 'none flagged this session'}. "
        f"Strong performance: {', '.join(strengths)}. "
        f"{review} {next_preview}"
    )

    return LessonWrapUp(
        todays_grammar=name,
        grammar_id=grammar_id,
        common_mistakes=tuple(common[:4]),
        strong_performance=tuple(strengths[:4]),
        suggested_review=review,
        next_lesson_preview=next_preview,
        summary_text=summary,
    )


def request_improved(state: CoachingSessionState) -> bool:
    return len(state.previous_hints) >= 2 or bool(state.diagnoses)
