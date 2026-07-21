"""Adaptive Intelligence orchestration — read-only over grammar engines.

Never calls mastery/progression write APIs. Never changes curriculum targets.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.language_adaptive_intelligence.confidence import build_confidence_views
from app.services.language_adaptive_intelligence.difficulty import decide_difficulty
from app.services.language_adaptive_intelligence.flags import (
    adaptive_intelligence_enabled,
    adaptive_profile_persist_enabled,
)
from app.services.language_adaptive_intelligence.parent import build_parent_insight
from app.services.language_adaptive_intelligence.profile import derive_learning_profile
from app.services.language_adaptive_intelligence.recommendations import (
    build_activity_mix,
    build_remediations,
    build_review_recommendations,
)
from app.services.language_adaptive_intelligence.signals import detect_learning_signals
from app.services.language_adaptive_intelligence.storage import (
    load_learning_profile,
    persist_learning_profile,
)
from app.services.language_adaptive_intelligence.teacher import build_teacher_insight
from app.services.language_adaptive_intelligence.types import (
    ActivityMixWeights,
    AdaptiveIntelligenceBundle,
    ParentInsight,
    StudentLearningProfile,
    TeacherInsight,
)
from app.services.language_grammar_catalog.catalog import get_default_catalog
from app.services.language_grammar_mastery import get_grammar_mastery_snapshot
from app.services.language_grammar_mastery.types import GrammarMasterySnapshot
from app.services.language_grammar_progression import get_grammar_progression_snapshot
from app.services.language_grammar_progression.types import GrammarProgressionSnapshot
from app.services.language_grammar_review import compute_from_mastery
from app.services.language_grammar_review.types import GrammarReviewSnapshot


def _as_of_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_adaptive_bundle(
    *,
    student_id: int,
    language_id: int,
    mastery: GrammarMasterySnapshot,
    progression: GrammarProgressionSnapshot | None = None,
    review: GrammarReviewSnapshot | None = None,
    prior_profile: StudentLearningProfile | None = None,
    as_of: str | None = None,
    force_enabled: bool = False,
) -> AdaptiveIntelligenceBundle:
    """Pure adaptive assembly — identical inputs ⇒ identical recommendations."""
    stamp = as_of or _as_of_now()
    catalog = get_default_catalog()
    enabled = bool(force_enabled or adaptive_intelligence_enabled())

    if not enabled:
        empty_profile = StudentLearningProfile(
            student_id=student_id,
            language_id=language_id,
            curriculum_version=str(catalog.version),
            updated_at=stamp,
        )
        return AdaptiveIntelligenceBundle(
            student_id=student_id,
            language_id=language_id,
            as_of=stamp,
            profile=empty_profile,
            enabled=False,
            current_grammar_id=progression.current_grammar_id if progression else None,
        )

    profile = derive_learning_profile(
        mastery,
        as_of=stamp,
        curriculum_version=str(catalog.version),
        prior=prior_profile,
    )
    signals = detect_learning_signals(mastery, as_of=stamp)
    confidence_views = build_confidence_views(mastery, as_of=stamp)
    current_id = progression.current_grammar_id if progression else None
    record = mastery.record_for(current_id) if current_id else None
    if record is None and mastery.records:
        # Prefer first weak topic for difficulty scaffolding when no sticky current.
        if profile.weak_grammar_ids:
            record = mastery.record_for(profile.weak_grammar_ids[0])
        if record is None:
            record = mastery.records[0]
        current_id = record.grammar_id

    difficulty = decide_difficulty(record, as_of=stamp, profile=profile)
    review_recs = build_review_recommendations(
        mastery, as_of=stamp, review=review
    )
    mix = build_activity_mix(
        mastery, as_of=stamp, current_grammar_id=current_id
    )
    remediations = build_remediations(signals, mastery, as_of=stamp)
    teacher = build_teacher_insight(
        mastery=mastery,
        progression=progression,
        profile=profile,
        signals=signals,
        confidence_views=confidence_views,
    )
    parent = build_parent_insight(
        mastery=mastery,
        progression=progression,
        review_recommendations=review_recs,
    )

    return AdaptiveIntelligenceBundle(
        student_id=student_id,
        language_id=language_id,
        as_of=stamp,
        profile=profile,
        signals=signals,
        confidence_views=confidence_views,
        difficulty=difficulty,
        review_recommendations=review_recs,
        activity_mix=mix,
        remediations=remediations,
        teacher=teacher,
        parent=parent,
        current_grammar_id=current_id,
        enabled=True,
    )


async def build_adaptive_bundle_async(
    db: AsyncSession,
    *,
    student_id: int,
    language_id: int = 1,
    as_of: str | None = None,
    persist_profile: bool | None = None,
) -> AdaptiveIntelligenceBundle:
    """Load grammar snapshots (read-only) and assemble adaptive advice."""
    stamp = as_of or _as_of_now()
    mastery = await get_grammar_mastery_snapshot(
        db, student_id=student_id, language_id=language_id
    )
    progression = await get_grammar_progression_snapshot(
        db, student_id=student_id, language_id=language_id
    )
    review = compute_from_mastery(mastery=mastery, as_of=stamp)
    prior = await load_learning_profile(
        db, student_id=student_id, language_id=language_id
    )

    bundle = build_adaptive_bundle(
        student_id=student_id,
        language_id=language_id,
        mastery=mastery,
        progression=progression,
        review=review,
        prior_profile=prior,
        as_of=stamp,
    )

    do_persist = (
        adaptive_profile_persist_enabled()
        if persist_profile is None
        else bool(persist_profile)
    )
    if bundle.enabled and do_persist:
        await persist_learning_profile(db, bundle.profile)

    return bundle


def empty_adaptive_bundle(*, student_id: int, language_id: int = 1) -> AdaptiveIntelligenceBundle:
    stamp = _as_of_now()
    return AdaptiveIntelligenceBundle(
        student_id=student_id,
        language_id=language_id,
        as_of=stamp,
        profile=StudentLearningProfile(
            student_id=student_id,
            language_id=language_id,
            updated_at=stamp,
        ),
        activity_mix=ActivityMixWeights(),
        teacher=TeacherInsight(),
        parent=ParentInsight(),
        enabled=False,
    )
