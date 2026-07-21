"""Tutor safety rules — reject educational inconsistencies; fail closed."""

from __future__ import annotations

from app.services.language_ai_tutor.enums import TutorSafetyCode
from app.services.language_ai_tutor.types import TutorContext, TutorGrammarSurface


def validate_tutor_grammar_focus(
    *,
    claimed_grammar_id: str | None,
    authoritative_grammar_id: str | None,
    grammar_surface: TutorGrammarSurface | None,
) -> tuple[TutorSafetyCode, str]:
    """Fail closed when resolver/runtime provides no grammar or claims diverge."""
    auth = (authoritative_grammar_id or "").strip() or None
    claim = (claimed_grammar_id or "").strip() or None

    if not auth and grammar_surface is None:
        return (
            TutorSafetyCode.no_grammar,
            "No grammar target is available for tutoring. Fail closed — do not invent a lesson.",
        )

    focus = auth or (grammar_surface.grammar_id if grammar_surface else None)
    if not focus:
        return (
            TutorSafetyCode.no_grammar,
            "Resolver returned no grammar. Fail closed.",
        )

    if claim and claim != focus:
        return (
            TutorSafetyCode.grammar_mismatch,
            f"Requested grammar '{claim}' does not match current lesson grammar '{focus}'.",
        )

    if grammar_surface and grammar_surface.grammar_id != focus:
        return (
            TutorSafetyCode.curriculum_contradiction,
            "Grammar surface does not match authoritative current grammar.",
        )

    return TutorSafetyCode.ok, ""


def apply_safety_to_context(ctx: TutorContext) -> TutorContext:
    """Stamp safety onto an assembled context (immutable replace)."""
    code, message = validate_tutor_grammar_focus(
        claimed_grammar_id=None,
        authoritative_grammar_id=ctx.grammar.grammar_id if ctx.grammar else None,
        grammar_surface=ctx.grammar,
    )
    if code is TutorSafetyCode.ok:
        return ctx
    return TutorContext(
        student_id=ctx.student_id,
        language_id=ctx.language_id,
        as_of=ctx.as_of,
        student_language=ctx.student_language,
        curriculum_version=ctx.curriculum_version,
        grammar=ctx.grammar,
        session=ctx.session,
        adaptive=ctx.adaptive,
        memory=ctx.memory,
        teacher_persona=ctx.teacher_persona,
        explanation_style=ctx.explanation_style,
        explainability_note=ctx.explainability_note,
        safety_code=code,
        safety_message=message,
        schema_version=ctx.schema_version,
    )


def utterance_allowed(ctx: TutorContext) -> bool:
    return ctx.safety_code is TutorSafetyCode.ok and ctx.grammar is not None
