"""Conversational Coaching orchestration (Wave E2).

READ: E1 TutorContext (+ adaptive projections inside it)
WRITE: coaching session state under ai_tutor_coaching only
NEVER: mastery, progression, resolver, evidence, curriculum, adaptive, E1 memory modules
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.language_ai_tutor import (
    TutorTurnRequest,
    build_tutor_context_async,
    build_tutor_context_pure,
)
from app.services.language_ai_tutor.enums import TutorPromptKind, TutorSafetyCode
from app.services.language_ai_tutor.types import TutorContext
from app.services.language_ai_tutor_coaching.enums import CoachingMove, HintLevel
from app.services.language_ai_tutor_coaching.flags import (
    coaching_state_persist_enabled,
    conversational_coaching_enabled,
)
from app.services.language_ai_tutor_coaching.hints import HINT_LADDER, build_hint_step
from app.services.language_ai_tutor_coaching.llm import generate_coaching_utterance
from app.services.language_ai_tutor_coaching.motivation import motivation_line
from app.services.language_ai_tutor_coaching.progression import (
    apply_decision_to_state,
    empty_coaching_state,
    vary_if_repeat,
)
from app.services.language_ai_tutor_coaching.prompts import (
    build_coaching_prompt,
    template_coaching_utterance,
)
from app.services.language_ai_tutor_coaching.reflection import reflection_question
from app.services.language_ai_tutor_coaching.socratic import (
    avoids_immediate_answer,
    compose_guided_utterance,
    opening_socratic_question,
)
from app.services.language_ai_tutor_coaching.storage import (
    load_coaching_state,
    persist_coaching_state,
)
from app.services.language_ai_tutor_coaching.strategy import decide_coaching_move
from app.services.language_ai_tutor_coaching.types import (
    CoachingSessionState,
    CoachingTurnRequest,
    CoachingTurnResponse,
    LessonWrapUp,
)
from app.services.language_ai_tutor_coaching.wrapup import build_lesson_wrap_up


def _to_e1_request(request: CoachingTurnRequest) -> TutorTurnRequest:
    return TutorTurnRequest(
        student_id=request.student_id,
        language_id=request.language_id,
        message=request.message,
        prompt_kind=TutorPromptKind.hint,
        conversation_id=request.conversation_id,
        grammar_id=request.grammar_id,
        lesson_id=request.lesson_id,
        activity_id=request.activity_id,
        step_id=request.step_id,
        student_language=request.student_language,
        as_of=request.as_of,
    )


def respond_coaching_turn_pure(
    ctx: TutorContext,
    state: CoachingSessionState,
    request: CoachingTurnRequest,
    *,
    next_grammar_id: str | None = None,
) -> tuple[CoachingTurnResponse, CoachingSessionState]:
    """Pure coaching turn for tests — no I/O."""
    if ctx.safety_code is not TutorSafetyCode.ok or ctx.grammar is None:
        return (
            CoachingTurnResponse(
                utterance=ctx.safety_message or "I can only coach on your current lesson grammar.",
                move=CoachingMove.encourage,
                hint_level=None,
                explanation_variety="step_by_step",
                diagnosis_kind=None,
                session_id=state.session_id,
                grammar_id=None,
                provider="safety",
                safety_code=ctx.safety_code.value,
            ),
            state,
        )

    # Align session anchors
    if not state.grammar_id and ctx.grammar:
        state = CoachingSessionState(
            student_id=state.student_id,
            language_id=state.language_id,
            session_id=state.session_id,
            grammar_id=ctx.grammar.grammar_id,
            activity_id=request.activity_id or state.activity_id,
            hint_level_index=state.hint_level_index,
            previous_hints=state.previous_hints,
            previous_explanations=state.previous_explanations,
            previous_mistakes=state.previous_mistakes,
            diagnoses=state.diagnoses,
            reflection_pending=state.reflection_pending,
            last_move=state.last_move,
            last_utterance_fingerprint=state.last_utterance_fingerprint,
            encouragement_count=state.encouragement_count,
            schema_version=state.schema_version,
            updated_at=state.updated_at,
        )

    decision = decide_coaching_move(ctx, state, request)
    wrap: LessonWrapUp | None = None
    hint_step = None
    if decision.hint_level is not None:
        hint_step = build_hint_step(ctx, decision.hint_level)

    low_conf = (ctx.adaptive.learning_confidence_current or ctx.adaptive.average_confidence or 0) < 45
    motivation = (
        motivation_line(
            ctx,
            state,
            just_improved=request.is_correct is True,
            after_mistake=request.is_correct is False,
            low_confidence=low_conf,
        )
        if decision.include_motivation or decision.move is CoachingMove.encourage
        else ""
    )
    reflect_q = (
        reflection_question(ctx, variant=len(state.previous_explanations))
        if decision.include_reflection or decision.move is CoachingMove.reflect
        else ""
    )

    if decision.move is CoachingMove.wrap_up:
        wrap = build_lesson_wrap_up(ctx, state, next_grammar_id=next_grammar_id)
        utterance = wrap.summary_text
    elif decision.move is CoachingMove.question:
        q = opening_socratic_question(ctx, hint_index=0)
        utterance = compose_guided_utterance(
            lead=motivation if decision.include_motivation else "",
            hint=hint_step,
            prefer_question_first=True,
        )
        if hint_step is None:
            utterance = f"{q} Take a moment before we look at a fuller hint."
    else:
        utterance = template_coaching_utterance(
            ctx,
            decision,
            hint_text=hint_step.text if hint_step else "",
            socratic_question=hint_step.socratic_question if hint_step else opening_socratic_question(ctx),
            reflection_q=reflect_q,
            motivation=motivation,
            wrap_summary=wrap.summary_text if wrap else "",
        )

    utterance = vary_if_repeat(state, utterance)
    if decision.avoid_immediate_answer and not avoids_immediate_answer(utterance):
        utterance = (
            (hint_step.socratic_question if hint_step else opening_socratic_question(ctx))
            + " "
            + utterance
        )

    new_state = apply_decision_to_state(
        state,
        decision,
        utterance=utterance,
        hint_text=hint_step.text if hint_step else None,
        diagnosis=decision.diagnosis,
    )

    return (
        CoachingTurnResponse(
            utterance=utterance,
            move=decision.move,
            hint_level=decision.hint_level.value if decision.hint_level else None,
            explanation_variety=decision.explanation_variety.value,
            diagnosis_kind=decision.diagnosis.kind.value if decision.diagnosis else None,
            diagnosis_why=decision.diagnosis.why if decision.diagnosis else "",
            reflection_question=reflect_q,
            motivation_line=motivation,
            explainability_note=ctx.explainability_note,
            reasons=decision.reasons,
            session_id=new_state.session_id,
            grammar_id=ctx.grammar.grammar_id if ctx.grammar else None,
            provider="template_fallback",
            wrap_up=wrap,
            safety_code=ctx.safety_code.value,
        ),
        new_state,
    )


async def respond_coaching_turn(
    db: AsyncSession,
    request: CoachingTurnRequest,
) -> CoachingTurnResponse:
    if not conversational_coaching_enabled():
        return CoachingTurnResponse(
            utterance="Conversational coaching is disabled.",
            move=CoachingMove.encourage,
            hint_level=None,
            explanation_variety="step_by_step",
            diagnosis_kind=None,
            provider="disabled",
            safety_code="disabled",
        )

    e1_req = _to_e1_request(request)
    ctx = await build_tutor_context_async(db, e1_req)

    state = await load_coaching_state(
        db,
        student_id=request.student_id,
        language_id=request.language_id,
        session_id=request.session_id,
    )
    if state is None:
        state = empty_coaching_state(
            student_id=request.student_id,
            language_id=request.language_id,
            session_id=request.session_id,
            grammar_id=request.grammar_id or (ctx.grammar.grammar_id if ctx.grammar else ""),
            activity_id=request.activity_id or "",
        )

    response, new_state = respond_coaching_turn_pure(ctx, state, request)

    # Optional LLM polish (still constrained by decision); keep template if safety/wrap_up
    if (
        response.provider == "template_fallback"
        and response.safety_code == "ok"
        and response.move is not CoachingMove.wrap_up
    ):
        decision = decide_coaching_move(ctx, state, request)
        prompt = build_coaching_prompt(
            ctx, decision, state, student_message=request.message
        )
        polished, provider, refl, motiv = await generate_coaching_utterance(
            prompt, fallback=response.utterance
        )
        if provider != "template_fallback":
            polished = vary_if_repeat(state, polished)
            if decision.avoid_immediate_answer and not avoids_immediate_answer(polished):
                polished = response.utterance
            response = CoachingTurnResponse(
                utterance=polished,
                move=response.move,
                hint_level=response.hint_level,
                explanation_variety=response.explanation_variety,
                diagnosis_kind=response.diagnosis_kind,
                diagnosis_why=response.diagnosis_why,
                reflection_question=refl or response.reflection_question,
                motivation_line=motiv or response.motivation_line,
                explainability_note=response.explainability_note,
                reasons=response.reasons,
                session_id=response.session_id,
                grammar_id=response.grammar_id,
                provider=provider,
                wrap_up=response.wrap_up,
                safety_code=response.safety_code,
            )
            new_state = apply_decision_to_state(
                state,
                decision,
                utterance=response.utterance,
                hint_text=None,
                diagnosis=decision.diagnosis,
            )

    if coaching_state_persist_enabled():
        await persist_coaching_state(db, new_state)

    return response


def build_coaching_context_pure(
    request: CoachingTurnRequest,
    *,
    progression=None,
    adaptive=None,
    force_enabled: bool = True,
) -> TutorContext:
    """Test helper: assemble E1 tutor context without DB."""
    return build_tutor_context_pure(
        _to_e1_request(request),
        progression=progression,
        adaptive=adaptive,
        force_enabled=force_enabled,
    )


# Re-export ladder for verify scripts
__all__ = [
    "HINT_LADDER",
    "HintLevel",
    "respond_coaching_turn",
    "respond_coaching_turn_pure",
    "build_coaching_context_pure",
]
