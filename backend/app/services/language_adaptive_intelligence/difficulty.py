"""Adaptive difficulty — changes HOW to teach, never WHAT grammar."""

from __future__ import annotations

from app.services.language_adaptive_intelligence.confidence import learning_confidence_for_record
from app.services.language_adaptive_intelligence.enums import AdaptiveDifficulty
from app.services.language_adaptive_intelligence.types import (
    DifficultyDecision,
    ExplainableReason,
    StudentLearningProfile,
)
from app.services.language_grammar_mastery.types import GrammarMasteryRecord


def decide_difficulty(
    record: GrammarMasteryRecord | None,
    *,
    as_of: str,
    profile: StudentLearningProfile | None = None,
) -> DifficultyDecision | None:
    """Pick Easy / Normal / Advanced for the current grammar target."""
    if record is None:
        return None

    mastery = float(record.dimensions.overall_mastery)
    conf = learning_confidence_for_record(record, as_of=as_of)
    reasons: list[ExplainableReason] = []

    level = AdaptiveDifficulty.normal
    if mastery < 45.0 or conf < 40.0 or float(record.retention_risk) >= 0.6:
        level = AdaptiveDifficulty.easy
        reasons.append(
            ExplainableReason(
                code="support_needed",
                message="Mastery or confidence is still building — use easier scaffolds",
                weight=1.2,
            )
        )
    elif mastery >= 80.0 and conf >= 70.0 and float(record.retention_risk) < 0.35:
        level = AdaptiveDifficulty.advanced
        reasons.append(
            ExplainableReason(
                code="ready_challenge",
                message="Strong mastery with solid confidence — increase challenge",
                weight=1.1,
            )
        )
    else:
        reasons.append(
            ExplainableReason(
                code="balanced",
                message="Balanced mastery and confidence — keep normal difficulty",
                weight=1.0,
            )
        )

    if profile and profile.preferred_pace.value == "slow" and level == AdaptiveDifficulty.advanced:
        level = AdaptiveDifficulty.normal
        reasons.append(
            ExplainableReason(
                code="pace_preference",
                message="Preferred pace is slow — hold challenge at normal",
                weight=0.9,
            )
        )

    if level is AdaptiveDifficulty.easy:
        return DifficultyDecision(
            grammar_id=record.grammar_id,
            difficulty_level=level,
            vocabulary_richness="low",
            sentence_length="short",
            distractor_quality="soft",
            reading_complexity="simple",
            listening_speed="slow",
            writing_expectations="supported",
            reasons=tuple(reasons),
        )
    if level is AdaptiveDifficulty.advanced:
        return DifficultyDecision(
            grammar_id=record.grammar_id,
            difficulty_level=level,
            vocabulary_richness="high",
            sentence_length="long",
            distractor_quality="challenging",
            reading_complexity="rich",
            listening_speed="fast",
            writing_expectations="extended",
            reasons=tuple(reasons),
        )
    return DifficultyDecision(
        grammar_id=record.grammar_id,
        difficulty_level=level,
        vocabulary_richness="medium",
        sentence_length="medium",
        distractor_quality="balanced",
        reading_complexity="standard",
        listening_speed="normal",
        writing_expectations="standard",
        reasons=tuple(reasons),
    )
