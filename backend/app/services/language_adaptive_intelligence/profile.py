"""Student learning profile derivation — influences generation only."""

from __future__ import annotations

from datetime import datetime, timezone

from app.services.language_adaptive_intelligence.confidence import learning_confidence_for_record
from app.services.language_adaptive_intelligence.enums import ExplanationDepth, PreferredPace
from app.services.language_adaptive_intelligence.types import StudentLearningProfile
from app.services.language_grammar_mastery.types import GrammarMasterySnapshot


def _as_of_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def derive_learning_profile(
    mastery: GrammarMasterySnapshot,
    *,
    as_of: str | None = None,
    curriculum_version: str = "",
    prior: StudentLearningProfile | None = None,
) -> StudentLearningProfile:
    """Build a profile from mastery signals (deterministic). Never changes mastery."""
    stamp = as_of or _as_of_now()
    confidences: list[float] = []
    weak: list[tuple[float, str]] = []
    strong: list[tuple[float, str]] = []
    skill_hits: dict[str, int] = {}

    for rec in mastery.records:
        conf = learning_confidence_for_record(rec, as_of=stamp)
        confidences.append(conf)
        mastery_score = float(rec.dimensions.overall_mastery)
        composite = (mastery_score * 0.55) + (conf * 0.45)
        if composite < 50.0 and rec.evidence_count >= 1:
            weak.append((composite, rec.grammar_id))
        if mastery_score >= 80.0 and conf >= 65.0:
            strong.append((composite, rec.grammar_id))
        for skill in rec.skill_coverage:
            key = skill.value if hasattr(skill, "value") else str(skill)
            skill_hits[key] = skill_hits.get(key, 0) + 1

    weak.sort(key=lambda x: (x[0], x[1]))
    strong.sort(key=lambda x: (-x[0], x[1]))
    avg_conf = round(sum(confidences) / len(confidences), 2) if confidences else 0.0

    preferred_skills = tuple(
        skill for skill, _ in sorted(skill_hits.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    )

    # Pace / depth preferences: derive lightly; preserve prior explicit prefs when present.
    pace = prior.preferred_pace if prior else PreferredPace.steady
    depth = prior.preferred_explanation_depth if prior else ExplanationDepth.guided
    if avg_conf < 40.0:
        pace = PreferredPace.slow
        depth = ExplanationDepth.detailed
    elif avg_conf >= 75.0 and len(strong) >= 3:
        pace = PreferredPace.fast
        depth = ExplanationDepth.brief

    engagement = min(100.0, round(len(mastery.records) * 8.0 + avg_conf * 0.4, 2))
    streak = prior.learning_streak_days if prior else 0
    if mastery.records:
        # Proxy streak: count of topics with last_seen within 2 days (deterministic).
        recent = 0
        from app.services.language_adaptive_intelligence.confidence import days_since

        for rec in mastery.records:
            idle = days_since(stamp, rec.last_seen_at)
            if idle is not None and idle <= 2:
                recent += 1
        streak = max(streak, min(30, recent))

    return StudentLearningProfile(
        student_id=mastery.student_id,
        language_id=mastery.language_id,
        preferred_pace=pace,
        preferred_explanation_depth=depth,
        preferred_examples=prior.preferred_examples if prior else "everyday",
        weak_grammar_ids=tuple(gid for _, gid in weak[:8]),
        strong_grammar_ids=tuple(gid for _, gid in strong[:8]),
        average_confidence=avg_conf,
        average_response_time_seconds=prior.average_response_time_seconds if prior else 0.0,
        retry_frequency=prior.retry_frequency if prior else 0.0,
        preferred_activity_types=preferred_skills or (("reading", "speaking") if prior is None else prior.preferred_activity_types),
        learning_streak_days=int(streak),
        engagement_score=engagement,
        curriculum_version=curriculum_version,
        updated_at=stamp,
    )


def profile_to_dict(profile: StudentLearningProfile) -> dict:
    return {
        "student_id": profile.student_id,
        "language_id": profile.language_id,
        "preferred_pace": profile.preferred_pace.value,
        "preferred_explanation_depth": profile.preferred_explanation_depth.value,
        "preferred_examples": profile.preferred_examples,
        "weak_grammar_ids": list(profile.weak_grammar_ids),
        "strong_grammar_ids": list(profile.strong_grammar_ids),
        "average_confidence": profile.average_confidence,
        "average_response_time_seconds": profile.average_response_time_seconds,
        "retry_frequency": profile.retry_frequency,
        "preferred_activity_types": list(profile.preferred_activity_types),
        "learning_streak_days": profile.learning_streak_days,
        "engagement_score": profile.engagement_score,
        "schema_version": profile.schema_version,
        "curriculum_version": profile.curriculum_version,
        "updated_at": profile.updated_at,
    }


def profile_from_dict(raw: dict | None, *, student_id: int, language_id: int) -> StudentLearningProfile | None:
    if not isinstance(raw, dict) or not raw:
        return None
    try:
        return StudentLearningProfile(
            student_id=int(raw.get("student_id") or student_id),
            language_id=int(raw.get("language_id") or language_id),
            preferred_pace=PreferredPace(str(raw.get("preferred_pace") or "steady")),
            preferred_explanation_depth=ExplanationDepth(
                str(raw.get("preferred_explanation_depth") or "guided")
            ),
            preferred_examples=str(raw.get("preferred_examples") or "everyday"),
            weak_grammar_ids=tuple(str(x) for x in (raw.get("weak_grammar_ids") or [])),
            strong_grammar_ids=tuple(str(x) for x in (raw.get("strong_grammar_ids") or [])),
            average_confidence=float(raw.get("average_confidence") or 0.0),
            average_response_time_seconds=float(raw.get("average_response_time_seconds") or 0.0),
            retry_frequency=float(raw.get("retry_frequency") or 0.0),
            preferred_activity_types=tuple(str(x) for x in (raw.get("preferred_activity_types") or [])),
            learning_streak_days=int(raw.get("learning_streak_days") or 0),
            engagement_score=float(raw.get("engagement_score") or 0.0),
            schema_version=int(raw.get("schema_version") or 1),
            curriculum_version=str(raw.get("curriculum_version") or ""),
            updated_at=str(raw.get("updated_at") or ""),
        )
    except (TypeError, ValueError):
        return None
