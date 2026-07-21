"""Coaching strategy — decide Explain / Hint / Question / Challenge / etc.

Uses TutorContext (profile, confidence, weakness, activity, grammar) + coaching state.
Never modifies educational engines.
"""

from __future__ import annotations

from app.services.language_ai_tutor.types import TutorContext
from app.services.language_ai_tutor_coaching.diagnosis import diagnose_mistake
from app.services.language_ai_tutor_coaching.enums import (
    CoachingMove,
    HintLevel,
    StudentIntent,
)
from app.services.language_ai_tutor_coaching.hints import HINT_LADDER, resolve_hint_level_index
from app.services.language_ai_tutor_coaching.intent import detect_intent
from app.services.language_ai_tutor_coaching.reflection import should_request_reflection
from app.services.language_ai_tutor_coaching.types import (
    CoachingDecision,
    CoachingSessionState,
    CoachingTurnRequest,
)
from app.services.language_ai_tutor_coaching.variety import choose_explanation_variety


def _confidence(ctx: TutorContext) -> float:
    if ctx.adaptive.learning_confidence_current is not None:
        return float(ctx.adaptive.learning_confidence_current)
    return float(ctx.adaptive.average_confidence or 0.0)


def decide_coaching_move(
    ctx: TutorContext,
    state: CoachingSessionState,
    request: CoachingTurnRequest,
) -> CoachingDecision:
    intent = detect_intent(request)
    variety = choose_explanation_variety(ctx)
    conf = _confidence(ctx)
    low_conf = conf < 45.0
    high_conf = conf >= 75.0
    reasons: list[str] = []

    if intent is StudentIntent.request_wrap_up:
        reasons.append("Student requested lesson wrap-up.")
        return CoachingDecision(
            move=CoachingMove.wrap_up,
            explanation_variety=variety,
            intent=intent,
            reasons=tuple(reasons),
            avoid_immediate_answer=False,
            include_motivation=True,
        )

    if request.is_correct is True:
        reasons.append("Correct attempt — celebrate lightly and reflect.")
        include_reflect = should_request_reflection(
            just_solved=True,
            revealed_full_explanation=False,
            reflection_pending=state.reflection_pending,
        )
        move = CoachingMove.challenge if high_conf else CoachingMove.reflect
        if low_conf:
            move = CoachingMove.encourage
            reasons.append("Low confidence — smaller step with encouragement.")
        return CoachingDecision(
            move=move,
            explanation_variety=variety,
            intent=intent,
            reasons=tuple(reasons),
            avoid_immediate_answer=True,
            include_reflection=include_reflect,
            include_motivation=True,
        )

    if request.is_correct is False:
        diagnosis = diagnose_mistake(
            ctx, attempt=request.student_attempt, message=request.message
        )
        idx = resolve_hint_level_index(state, after_mistake=True)
        reasons.append(f"Incorrect attempt diagnosed as {diagnosis.kind.value}.")
        reasons.append("Guide with a hint before revealing the answer.")
        return CoachingDecision(
            move=CoachingMove.diagnose,
            hint_level=HINT_LADDER[idx],
            explanation_variety=variety,
            diagnosis=diagnosis,
            intent=intent,
            reasons=tuple(reasons),
            avoid_immediate_answer=True,
            include_motivation=True,
        )

    if intent is StudentIntent.request_full_answer:
        reasons.append("Student explicitly requested the full answer.")
        idx = resolve_hint_level_index(state, jump_to_full=True)
        level = HINT_LADDER[idx]
        # Allow worked example on second explicit request
        if state.hint_level_index >= HINT_LADDER.index(HintLevel.full_explanation):
            level = HintLevel.worked_example
            reasons.append("Escalate to worked example after full explanation.")
        return CoachingDecision(
            move=CoachingMove.explain,
            hint_level=level,
            explanation_variety=variety,
            intent=intent,
            reasons=tuple(reasons),
            avoid_immediate_answer=False,
            include_reflection=True,
        )

    if intent in {StudentIntent.ask_hint, StudentIntent.ask_answer, StudentIntent.general}:
        # Default: Socratic / hint — do not solve immediately
        idx = resolve_hint_level_index(
            state,
            asking_for_hint=intent is StudentIntent.ask_hint
            or intent is StudentIntent.ask_answer,
        )
        if not state.previous_hints and intent is StudentIntent.general:
            reasons.append("Open with a Socratic question before explaining.")
            return CoachingDecision(
                move=CoachingMove.question,
                hint_level=HINT_LADDER[0],
                explanation_variety=variety,
                intent=intent,
                reasons=tuple(reasons),
                avoid_immediate_answer=True,
                include_motivation=low_conf,
            )
        reasons.append("Escalate hints gradually; avoid immediate final answer.")
        if high_conf and len(state.previous_hints) >= 2:
            reasons.append("High confidence — offer a challenge extension.")
            return CoachingDecision(
                move=CoachingMove.challenge,
                hint_level=HINT_LADDER[idx],
                explanation_variety=variety,
                intent=intent,
                reasons=tuple(reasons),
                avoid_immediate_answer=True,
            )
        return CoachingDecision(
            move=CoachingMove.hint,
            hint_level=HINT_LADDER[idx],
            explanation_variety=variety,
            intent=intent,
            reasons=tuple(reasons),
            avoid_immediate_answer=True,
            include_motivation=low_conf,
        )

    if intent is StudentIntent.ask_why:
        reasons.append("Student asked why — explain with diagnosis-style clarity.")
        return CoachingDecision(
            move=CoachingMove.explain,
            hint_level=HintLevel.level_3,
            explanation_variety=variety,
            intent=intent,
            reasons=tuple(reasons),
            avoid_immediate_answer=True,
            include_reflection=True,
        )

    reasons.append("Default coaching move: guided question.")
    return CoachingDecision(
        move=CoachingMove.question,
        hint_level=HintLevel.level_1,
        explanation_variety=variety,
        intent=intent,
        reasons=tuple(reasons),
        avoid_immediate_answer=True,
    )
