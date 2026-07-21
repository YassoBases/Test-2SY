"""Tutor Context Builder — read-only assembly; never writes educational state."""

from __future__ import annotations

from datetime import datetime, timezone

from app.services.language_adaptive_intelligence.types import AdaptiveIntelligenceBundle
from app.services.language_ai_tutor.enums import TutorSafetyCode
from app.services.language_ai_tutor.explanation import decide_explanation_style
from app.services.language_ai_tutor.memory import memory_to_summary
from app.services.language_ai_tutor.persona import resolve_teacher_persona
from app.services.language_ai_tutor.safety import validate_tutor_grammar_focus
from app.services.language_ai_tutor.types import (
    ConversationMemory,
    TutorAdaptiveSurface,
    TutorContext,
    TutorGrammarSurface,
    TutorMemorySummary,
    TutorSessionAwareness,
    TutorTurnRequest,
)
from app.services.language_grammar_activity_authoring.types import TeacherPersona
from app.services.language_grammar_catalog.catalog import get_default_catalog, get_topic
from app.services.language_grammar_mastery.types import GrammarMasterySnapshot
from app.services.language_grammar_progression.types import GrammarProgressionSnapshot
from app.services.language_grammar_skill_context.types import SkillGrammarContext


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _grammar_from_topic(grammar_id: str) -> TutorGrammarSurface | None:
    topic = get_topic(grammar_id)
    if topic is None:
        return None
    return TutorGrammarSurface(
        grammar_id=topic.grammar_id,
        display_code=topic.display_code or "",
        display_name=topic.display_name,
        cefr_band=topic.cefr_band.value if hasattr(topic.cefr_band, "value") else str(topic.cefr_band),
        teaching_notes=topic.teaching_notes or topic.focus_note or "",
        examples=tuple(str(x) for x in topic.example_sentences[:4]),
        common_mistakes=tuple(str(x) for x in topic.common_errors[:4]),
        learning_objectives=tuple(str(x) for x in topic.learning_objectives[:4]),
    )


def grammar_from_skill_context(ctx: SkillGrammarContext) -> TutorGrammarSurface:
    return TutorGrammarSurface(
        grammar_id=ctx.grammar_id,
        display_code=ctx.display_code,
        display_name=ctx.display_name,
        cefr_band=ctx.cefr_band.value if hasattr(ctx.cefr_band, "value") else str(ctx.cefr_band),
        teaching_notes=ctx.teaching_notes or ctx.focus_note,
        examples=tuple(ctx.examples[:4]),
        common_mistakes=tuple(ctx.common_mistakes[:4]),
        learning_objectives=tuple(ctx.learning_objectives[:4]),
    )


def project_adaptive_surface(
    adaptive: AdaptiveIntelligenceBundle | None,
    *,
    grammar_id: str | None,
) -> TutorAdaptiveSurface:
    """Copy adaptive fields into a prompt-safe surface (no live objects)."""
    if adaptive is None or not adaptive.enabled:
        return TutorAdaptiveSurface()

    conf_current = None
    mastery_current = None
    if grammar_id:
        for view in adaptive.confidence_views:
            if view.grammar_id == grammar_id:
                conf_current = view.learning_confidence
                mastery_current = view.mastery_score
                break

    notes: list[str] = []
    if adaptive.difficulty and adaptive.difficulty.reasons:
        notes.extend(r.message for r in adaptive.difficulty.reasons[:2])
    for rem in adaptive.remediations[:2]:
        if rem.explanation:
            notes.append(rem.explanation.split("\n")[0])

    return TutorAdaptiveSurface(
        preferred_pace=adaptive.profile.preferred_pace.value,
        preferred_explanation_depth=adaptive.profile.preferred_explanation_depth.value,
        preferred_examples=adaptive.profile.preferred_examples,
        average_confidence=adaptive.profile.average_confidence,
        weak_grammar_ids=adaptive.profile.weak_grammar_ids,
        strong_grammar_ids=adaptive.profile.strong_grammar_ids,
        difficulty_level=(
            adaptive.difficulty.difficulty_level.value if adaptive.difficulty else "normal"
        ),
        learning_confidence_current=conf_current,
        mastery_score_current=mastery_current,
        review_horizons=tuple(r.horizon.value for r in adaptive.review_recommendations[:5]),
        weakness_signal_kinds=tuple(s.kind.value for s in adaptive.signals[:8]),
        remediation_kinds=tuple(m.kind.value for m in adaptive.remediations[:5]),
        activity_mix=adaptive.activity_mix.as_dict(),
        explainability_notes=tuple(notes[:4]),
    )


def resolve_authoritative_grammar_id(
    *,
    progression: GrammarProgressionSnapshot | None,
    adaptive: AdaptiveIntelligenceBundle | None,
    session_grammar_id: str | None,
) -> str | None:
    """Prefer session → progression → adaptive. Request grammar is a claim, not authority."""
    for candidate in (
        session_grammar_id,
        progression.current_grammar_id if progression else None,
        adaptive.current_grammar_id if adaptive else None,
    ):
        if candidate and str(candidate).strip():
            return str(candidate).strip()
    return None


def build_tutor_context(
    *,
    student_id: int,
    language_id: int,
    request: TutorTurnRequest | None = None,
    mastery: GrammarMasterySnapshot | None = None,  # accepted for future; never written
    progression: GrammarProgressionSnapshot | None = None,
    adaptive: AdaptiveIntelligenceBundle | None = None,
    skill_grammar: SkillGrammarContext | None = None,
    session: TutorSessionAwareness | None = None,
    memory: ConversationMemory | None = None,
    teacher_persona: TeacherPersona | None = None,
    as_of: str | None = None,
    student_language: str = "en",
) -> TutorContext:
    """Assemble read-only TutorContext. ``mastery`` is unused for writes — reserved for future projections."""
    del mastery  # explicit: tutor must not reason over raw mastery models in prompts
    stamp = as_of or (request.as_of if request else None) or _now()
    catalog = get_default_catalog()
    req = request
    session_view = session or TutorSessionAwareness(
        lesson_id=(req.lesson_id if req and req.lesson_id else ""),
        current_activity_id=(req.activity_id if req and req.activity_id else ""),
        current_step_id=(req.step_id if req and req.step_id else ""),
    )

    session_gid = None
    if skill_grammar is not None:
        session_gid = skill_grammar.grammar_id
    elif session_view.grammar_id:
        session_gid = session_view.grammar_id
    auth_gid = resolve_authoritative_grammar_id(
        progression=progression,
        adaptive=adaptive,
        session_grammar_id=session_gid,
    )
    # Only when no lesson/progression authority exists may an explicit request
    # supply a focus grammar (still catalog-validated). Never overrides a live lesson.
    if not auth_gid and req and req.grammar_id:
        auth_gid = str(req.grammar_id).strip() or None

    claim = req.grammar_id if req else None
    grammar_surface: TutorGrammarSurface | None = None
    if skill_grammar is not None:
        grammar_surface = grammar_from_skill_context(skill_grammar)
    elif auth_gid:
        grammar_surface = _grammar_from_topic(auth_gid)

    code, message = validate_tutor_grammar_focus(
        claimed_grammar_id=claim,
        authoritative_grammar_id=auth_gid or (grammar_surface.grammar_id if grammar_surface else None),
        grammar_surface=grammar_surface,
    )

    adaptive_surface = project_adaptive_surface(
        adaptive, grammar_id=grammar_surface.grammar_id if grammar_surface else auth_gid
    )
    # Overlay conversational preference hints from memory when present
    if memory is not None:
        adaptive_surface = TutorAdaptiveSurface(
            preferred_pace=adaptive_surface.preferred_pace,
            preferred_explanation_depth=memory.explanation_preference
            or adaptive_surface.preferred_explanation_depth,
            preferred_examples=memory.preferred_examples or adaptive_surface.preferred_examples,
            average_confidence=adaptive_surface.average_confidence,
            weak_grammar_ids=adaptive_surface.weak_grammar_ids,
            strong_grammar_ids=adaptive_surface.strong_grammar_ids,
            difficulty_level=adaptive_surface.difficulty_level,
            learning_confidence_current=adaptive_surface.learning_confidence_current,
            mastery_score_current=adaptive_surface.mastery_score_current,
            review_horizons=adaptive_surface.review_horizons,
            weakness_signal_kinds=adaptive_surface.weakness_signal_kinds,
            remediation_kinds=adaptive_surface.remediation_kinds,
            activity_mix=adaptive_surface.activity_mix,
            explainability_notes=adaptive_surface.explainability_notes,
        )

    style, explain_note = decide_explanation_style(adaptive_surface)
    persona = resolve_teacher_persona(
        teacher_persona or (req.teacher_persona if req else None)
    )
    mem_summary = (
        memory_to_summary(memory)
        if memory
        else TutorMemorySummary(
            preferred_tone="supportive",
            preferred_examples=adaptive_surface.preferred_examples,
            explanation_preference=adaptive_surface.preferred_explanation_depth,
        )
    )

    if code is not TutorSafetyCode.ok:
        return TutorContext(
            student_id=student_id,
            language_id=language_id,
            as_of=stamp,
            student_language=student_language or (req.student_language if req else "en"),
            curriculum_version=str(catalog.version),
            grammar=grammar_surface,
            session=session_view,
            adaptive=adaptive_surface,
            memory=mem_summary,
            teacher_persona=persona,
            explanation_style=style,
            explainability_note=explain_note,
            safety_code=code,
            safety_message=message,
        )

    # Session objective from grammar when missing
    if not session_view.lesson_objective and grammar_surface:
        obj = grammar_surface.learning_objectives[0] if grammar_surface.learning_objectives else (
            f"Practice {grammar_surface.display_name}"
        )
        session_view = TutorSessionAwareness(
            lesson_id=session_view.lesson_id or (req.lesson_id if req and req.lesson_id else ""),
            lesson_objective=obj,
            grammar_id=session_view.grammar_id or grammar_surface.grammar_id,
            current_activity_id=session_view.current_activity_id,
            current_step_id=session_view.current_step_id,
            completed_activity_ids=session_view.completed_activity_ids,
            remaining_activity_ids=session_view.remaining_activity_ids,
            runtime_state=session_view.runtime_state,
        )

    return TutorContext(
        student_id=student_id,
        language_id=language_id,
        as_of=stamp,
        student_language=student_language or (req.student_language if req else "en"),
        curriculum_version=str(catalog.version),
        grammar=grammar_surface,
        session=session_view,
        adaptive=adaptive_surface,
        memory=mem_summary,
        teacher_persona=persona,
        explanation_style=style,
        explainability_note=explain_note,
        safety_code=TutorSafetyCode.ok,
        safety_message="",
    )

