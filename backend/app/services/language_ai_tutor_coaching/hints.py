"""Multi-level hint engine — escalate; never skip to the answer unless requested."""

from __future__ import annotations

from app.services.language_ai_tutor.types import TutorContext
from app.services.language_ai_tutor_coaching.enums import HintLevel
from app.services.language_ai_tutor_coaching.types import CoachingSessionState, HintStep

HINT_LADDER: tuple[HintLevel, ...] = (
    HintLevel.level_1,
    HintLevel.level_2,
    HintLevel.level_3,
    HintLevel.full_explanation,
    HintLevel.worked_example,
)


def clamp_hint_index(index: int) -> int:
    return max(0, min(int(index), len(HINT_LADDER) - 1))


def resolve_hint_level_index(
    state: CoachingSessionState,
    *,
    jump_to_full: bool = False,
    asking_for_hint: bool = False,
    after_mistake: bool = False,
) -> int:
    """Escalate one rung at a time. Full answer only when explicitly requested."""
    if jump_to_full:
        return HINT_LADDER.index(HintLevel.full_explanation)

    if asking_for_hint or after_mistake:
        if not state.previous_hints:
            return 0
        # Do not jump past level_3 unless student asked for full answer.
        nxt = clamp_hint_index(state.hint_level_index + 1)
        max_auto = HINT_LADDER.index(HintLevel.level_3)
        return min(nxt, max_auto)

    return clamp_hint_index(state.hint_level_index)


def build_hint_step(ctx: TutorContext, level: HintLevel) -> HintStep:
    g = ctx.grammar
    name = g.display_name if g else "this grammar"
    example = g.examples[0] if g and g.examples else f"a clear {name} sentence"
    mistake = g.common_mistakes[0] if g and g.common_mistakes else "mixing up the time reference"
    notes = (g.teaching_notes if g and g.teaching_notes else f"Focus on the core pattern of {name}.")

    if level is HintLevel.level_1:
        return HintStep(
            level=level,
            text=f"Look closely at the verb form in the sentence about {name}.",
            socratic_question="What do you notice about the verb?",
        )
    if level is HintLevel.level_2:
        return HintStep(
            level=level,
            text=f"Think about the time meaning. {name} usually signals a specific time relationship.",
            socratic_question="What tense is the sentence describing?",
        )
    if level is HintLevel.level_3:
        return HintStep(
            level=level,
            text=f"Compare the events: one may happen before another. Avoid this common slip: {mistake}.",
            socratic_question="What happened first?",
        )
    if level is HintLevel.full_explanation:
        return HintStep(
            level=level,
            text=(
                f"Full explanation for {name}: {notes} "
                f"Use the pattern carefully and check the time meaning before choosing a form."
            ),
            socratic_question="Can you restate the rule in your own words?",
        )
    return HintStep(
        level=level,
        text=(
            f"Worked example for {name}: study this model — «{example}». "
            f"Notice how the verb form matches the meaning, then try a similar sentence."
        ),
        socratic_question="How would you change this example to talk about a different subject?",
    )
