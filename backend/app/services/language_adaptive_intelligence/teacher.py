"""Teacher insight projections — advisory only; never change curriculum."""

from __future__ import annotations

from app.services.language_adaptive_intelligence.enums import LearningSignalKind
from app.services.language_adaptive_intelligence.types import (
    ExplainableReason,
    LearningSignal,
    StudentLearningProfile,
    TeacherInsight,
    TopicConfidenceView,
)
from app.services.language_grammar_catalog.catalog import get_topic
from app.services.language_grammar_mastery.types import GrammarMasterySnapshot
from app.services.language_grammar_progression.types import GrammarProgressionSnapshot


def build_teacher_insight(
    *,
    mastery: GrammarMasterySnapshot,
    progression: GrammarProgressionSnapshot | None,
    profile: StudentLearningProfile,
    signals: tuple[LearningSignal, ...],
    confidence_views: tuple[TopicConfidenceView, ...],
) -> TeacherInsight:
    """Summarize struggles, strengths, and retention risks for teachers."""
    struggle_names: list[str] = []
    for gid in profile.weak_grammar_ids[:5]:
        topic = get_topic(gid)
        struggle_names.append(topic.display_name if topic else gid)

    # Also surface recurring-mistake signal topics not already listed
    for sig in signals:
        if sig.kind is LearningSignalKind.recurring_mistakes and sig.display_name not in struggle_names:
            struggle_names.append(sig.display_name)
        if len(struggle_names) >= 6:
            break

    skill_hits: dict[str, int] = {}
    for rec in mastery.records:
        for skill in rec.skill_coverage:
            key = skill.value if hasattr(skill, "value") else str(skill)
            if float(rec.dimensions.overall_mastery) >= 70.0:
                skill_hits[key] = skill_hits.get(key, 0) + 1
    strength_skills = tuple(
        skill for skill, _ in sorted(skill_hits.items(), key=lambda kv: (-kv[1], kv[0]))[:4]
    )
    if not strength_skills and profile.preferred_activity_types:
        strength_skills = tuple(profile.preferred_activity_types[:3])

    risk_notes: list[str] = []
    for view in confidence_views:
        if view.retention_risk >= 0.55 or (
            view.mastery_score >= 60.0 and view.learning_confidence < 45.0
        ):
            risk_notes.append(
                f"May forget {view.display_name} soon "
                f"(confidence {view.learning_confidence:.0f}%, retention risk {view.retention_risk:.2f})."
            )
        if len(risk_notes) >= 4:
            break

    focus_id = progression.current_grammar_id if progression else None
    focus_name = ""
    if focus_id:
        topic = get_topic(focus_id)
        focus_name = topic.display_name if topic else focus_id

    explanations = (
        ExplainableReason(
            code="teacher_struggles",
            message=f"Struggles inferred from low composite mastery+confidence: {', '.join(struggle_names) or 'none flagged'}",
        ),
        ExplainableReason(
            code="teacher_strengths",
            message=f"Strength skills from high-mastery coverage: {', '.join(strength_skills) or 'still building'}",
        ),
    )

    return TeacherInsight(
        struggling_topics=tuple(struggle_names[:6]),
        strength_skills=strength_skills,
        risk_notes=tuple(risk_notes),
        focus_grammar_id=focus_id,
        focus_display_name=focus_name,
        explanations=explanations,
    )


def teacher_insight_to_dict(insight: TeacherInsight) -> dict:
    return {
        "struggling_topics": list(insight.struggling_topics),
        "strength_skills": list(insight.strength_skills),
        "risk_notes": list(insight.risk_notes),
        "focus_grammar_id": insight.focus_grammar_id,
        "focus_display_name": insight.focus_display_name,
        "explanations": [r.message for r in insight.explanations],
        "advisory_only": True,
    }
