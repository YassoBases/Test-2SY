"""AI Tutor Foundation orchestration — communicate existing intelligence only.

READ: mastery / progression / adaptive / catalog / skill grammar / runtime projection
WRITE: conversation memory under ai_tutor JSONB only
NEVER: mastery, progression, resolver, evidence, curriculum, adaptive profile
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.language_adaptive_intelligence import (
    build_adaptive_bundle,
    build_adaptive_bundle_async,
)
from app.services.language_ai_tutor.context import build_tutor_context
from app.services.language_ai_tutor.enums import TutorPromptKind, TutorSafetyCode
from app.services.language_ai_tutor.flags import (
    ai_tutor_enabled,
    ai_tutor_memory_persist_enabled,
)
from app.services.language_ai_tutor.llm import generate_tutor_utterance
from app.services.language_ai_tutor.memory import append_turn, empty_memory
from app.services.language_ai_tutor.prompts import build_prompt_bundle
from app.services.language_ai_tutor.safety import utterance_allowed
from app.services.language_ai_tutor.storage import (
    load_conversation_memory,
    persist_conversation_memory,
)
from app.services.language_ai_tutor.types import (
    TutorContext,
    TutorResponse,
    TutorSessionAwareness,
    TutorTurnRequest,
)
from app.services.language_grammar_mastery import get_grammar_mastery_snapshot
from app.services.language_grammar_progression import get_grammar_progression_snapshot
from app.services.language_grammar_skill_context import context_from_grammar_id
from app.services.language_grammar.enums import GrammarEvidenceSourceSkill


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _session_from_runtime(session_obj) -> TutorSessionAwareness:
    """Project runtime session without mutating it."""
    if session_obj is None:
        return TutorSessionAwareness()
    cursor = getattr(session_obj, "cursor", None)
    step_id = ""
    if cursor is not None:
        step_id = str(getattr(cursor, "current_step_id", "") or "")
    return TutorSessionAwareness(
        lesson_id=str(getattr(session_obj, "lesson_id", "") or ""),
        grammar_id=str(getattr(session_obj, "grammar_id", "") or ""),
        current_activity_id=step_id,
        current_step_id=step_id,
        completed_activity_ids=tuple(getattr(session_obj, "completed_step_ids", ()) or ()),
        remaining_activity_ids=tuple(getattr(session_obj, "pending_step_ids", ()) or ()),
        runtime_state=str(
            getattr(getattr(session_obj, "state", None), "value", getattr(session_obj, "state", ""))
            or ""
        ),
    )


async def _load_runtime_projection(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int,
) -> TutorSessionAwareness:
    """Read-only runtime projection — no FOR UPDATE lock."""
    from sqlalchemy import select

    from app.models.language.progression import LanguageProgression
    from app.services.language_grammar_lesson_runtime.storage import (
        runtime_bucket_from_payload,
        session_from_bucket,
    )

    result = await db.execute(
        select(LanguageProgression).where(
            LanguageProgression.student_id == student_id,
            LanguageProgression.language_id == language_id,
        )
    )
    row = result.scalar_one_or_none()
    if row is None:
        return TutorSessionAwareness()
    bucket = runtime_bucket_from_payload(dict(row.promotion_readiness_json or {}))
    session = session_from_bucket(bucket)
    if session is None:
        return TutorSessionAwareness()
    return _session_from_runtime(session)


def build_tutor_context_pure(
    request: TutorTurnRequest,
    *,
    progression=None,
    adaptive=None,
    memory=None,
    session: TutorSessionAwareness | None = None,
    force_enabled: bool = False,
) -> TutorContext:
    """Pure context assembly for tests / offline verification."""
    if not force_enabled and not ai_tutor_enabled():
        return TutorContext(
            student_id=request.student_id,
            language_id=request.language_id,
            as_of=request.as_of or _now(),
            safety_code=TutorSafetyCode.disabled,
            safety_message="AI Tutor is disabled.",
        )

    skill = None
    # Authority order matches context builder (session → progression → adaptive).
    gid = None
    if session is not None and session.grammar_id:
        gid = session.grammar_id
    if not gid and progression is not None:
        gid = progression.current_grammar_id
    if not gid and adaptive is not None:
        gid = adaptive.current_grammar_id
    if not gid:
        gid = request.grammar_id
    if gid:
        try:
            skill = context_from_grammar_id(
                gid,
                source_skill=GrammarEvidenceSourceSkill.grammar_lesson,
            )
        except Exception:  # noqa: BLE001
            skill = None

    return build_tutor_context(
        student_id=request.student_id,
        language_id=request.language_id,
        request=request,
        progression=progression,
        adaptive=adaptive,
        skill_grammar=skill,
        session=session,
        memory=memory,
        teacher_persona=request.teacher_persona,
        as_of=request.as_of,
        student_language=request.student_language,
    )


async def build_tutor_context_async(
    db: AsyncSession,
    request: TutorTurnRequest,
) -> TutorContext:
    if not ai_tutor_enabled():
        return TutorContext(
            student_id=request.student_id,
            language_id=request.language_id,
            as_of=request.as_of or _now(),
            safety_code=TutorSafetyCode.disabled,
            safety_message="AI Tutor is disabled.",
        )

    progression = await get_grammar_progression_snapshot(
        db, student_id=request.student_id, language_id=request.language_id
    )
    # Read adaptive without persisting profile (tutor must not modify adaptive).
    try:
        adaptive = await build_adaptive_bundle_async(
            db,
            student_id=request.student_id,
            language_id=request.language_id,
            as_of=request.as_of,
            persist_profile=False,
        )
    except Exception:  # noqa: BLE001
        mastery = await get_grammar_mastery_snapshot(
            db, student_id=request.student_id, language_id=request.language_id
        )
        adaptive = build_adaptive_bundle(
            student_id=request.student_id,
            language_id=request.language_id,
            mastery=mastery,
            progression=progression,
            as_of=request.as_of,
            force_enabled=True,
        )

    memory = await load_conversation_memory(
        db,
        student_id=request.student_id,
        language_id=request.language_id,
        conversation_id=request.conversation_id,
    )
    session = await _load_runtime_projection(
        db, student_id=request.student_id, language_id=request.language_id
    )
    if request.lesson_id or request.activity_id or request.step_id or request.grammar_id:
        session = TutorSessionAwareness(
            lesson_id=request.lesson_id or session.lesson_id,
            lesson_objective=session.lesson_objective,
            grammar_id=request.grammar_id or session.grammar_id,
            current_activity_id=request.activity_id or session.current_activity_id,
            current_step_id=request.step_id or session.current_step_id,
            completed_activity_ids=session.completed_activity_ids,
            remaining_activity_ids=session.remaining_activity_ids,
            runtime_state=session.runtime_state,
        )

    return build_tutor_context_pure(
        request,
        progression=progression,
        adaptive=adaptive,
        memory=memory,
        session=session,
        force_enabled=True,
    )


async def respond_tutor_turn(
    db: AsyncSession,
    request: TutorTurnRequest,
) -> TutorResponse:
    """Full tutor turn: context → prompt → LLM/template → memory write only."""
    ctx = await build_tutor_context_async(db, request)
    kind = request.prompt_kind or TutorPromptKind.answer_question

    memory = await load_conversation_memory(
        db,
        student_id=request.student_id,
        language_id=request.language_id,
        conversation_id=request.conversation_id,
    )
    if memory is None:
        memory = empty_memory(
            student_id=request.student_id,
            language_id=request.language_id,
            conversation_id=request.conversation_id,
        )

    if not utterance_allowed(ctx):
        msg = ctx.safety_message or "I can only help with your current lesson grammar."
        return TutorResponse(
            utterance=msg,
            prompt_kind=kind,
            grammar_id=ctx.grammar.grammar_id if ctx.grammar else None,
            explanation_style=ctx.explanation_style,
            explainability_note=ctx.explainability_note,
            safety_code=ctx.safety_code,
            provider="safety",
            conversation_id=memory.conversation_id,
            context_as_of=ctx.as_of,
        )

    prompt = build_prompt_bundle(ctx, prompt_kind=kind, student_message=request.message)
    utterance, provider = await generate_tutor_utterance(
        ctx, prompt, student_message=request.message
    )

    if request.message.strip():
        memory = append_turn(
            memory,
            role="student",
            content=request.message,
            prompt_kind=kind.value,
        )
    memory = append_turn(
        memory,
        role="tutor",
        content=utterance,
        prompt_kind=kind.value,
        mark_unfinished="" if kind is not TutorPromptKind.answer_question else memory.unfinished_discussion,
    )

    if ai_tutor_memory_persist_enabled():
        await persist_conversation_memory(db, memory)

    return TutorResponse(
        utterance=utterance,
        prompt_kind=kind,
        grammar_id=ctx.grammar.grammar_id if ctx.grammar else None,
        explanation_style=ctx.explanation_style,
        explainability_note=ctx.explainability_note,
        safety_code=ctx.safety_code,
        provider=provider,
        conversation_id=memory.conversation_id,
        context_as_of=ctx.as_of,
    )
