"""Mistake diagnosis — explain WHY, not only WHAT. Deterministic heuristics."""

from __future__ import annotations

from app.services.language_ai_tutor.types import TutorContext
from app.services.language_ai_tutor_coaching.enums import MistakeKind
from app.services.language_ai_tutor_coaching.types import MistakeDiagnosis


def diagnose_mistake(
    ctx: TutorContext,
    *,
    attempt: str | None,
    message: str = "",
) -> MistakeDiagnosis:
    """Classify a wrong attempt using grammar surface + simple lexical cues."""
    g = ctx.grammar
    grammar_id = g.grammar_id if g else ""
    name = g.display_name if g else "the target grammar"
    text = f"{attempt or ''} {message}".strip().lower()
    notes: list[str] = []

    vocab_cues = ("meaning of", "what does", "vocabulary", "word means", "translate")
    reading_cues = ("the text says", "passage", "i read", "according to", "paragraph")
    careless_cues = ("oops", "typo", "misclick", "accident", "meant to", "careless")

    if any(c in text for c in careless_cues):
        kind = MistakeKind.careless_mistake
        why = (
            f"This looks like a careless slip rather than a misunderstanding of {name}. "
            f"Slow down and re-check the verb form against the time meaning."
        )
        notes.append("careless_cue")
    elif any(c in text for c in vocab_cues):
        kind = MistakeKind.vocabulary_misunderstanding
        why = (
            f"The miss may come from vocabulary, not the {name} rule itself. "
            f"Confirm key word meanings, then re-apply the grammar pattern."
        )
        notes.append("vocabulary_cue")
    elif any(c in text for c in reading_cues):
        kind = MistakeKind.reading_misunderstanding
        why = (
            f"This may be a reading misunderstanding of the situation, which then led to the wrong "
            f"{name} choice. Re-read what happened first, then choose the form."
        )
        notes.append("reading_cue")
    else:
        kind = MistakeKind.grammar_misconception
        common = g.common_mistakes[0] if g and g.common_mistakes else "the time/form mismatch"
        why = (
            f"This looks like a grammar misconception about {name}. "
            f"A common trap is: {common}. The form must match the intended time meaning."
        )
        notes.append("default_grammar")

    if g and g.common_mistakes:
        notes.append(f"catalog_mistake:{g.common_mistakes[0][:80]}")

    return MistakeDiagnosis(
        kind=kind,
        why=why,
        evidence_notes=tuple(notes),
        grammar_id=grammar_id,
    )


def diagnosis_consistent(a: MistakeDiagnosis, b: MistakeDiagnosis) -> bool:
    """Same inputs ⇒ same kind (used by verification)."""
    return a.kind == b.kind and a.grammar_id == b.grammar_id
