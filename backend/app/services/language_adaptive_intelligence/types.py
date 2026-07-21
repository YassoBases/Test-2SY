"""Adaptive Learning Intelligence contracts (Phase 2).

Read-only educational adaptation — never writes mastery/progression/curriculum.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.services.language_adaptive_intelligence.enums import (
    AdaptiveDifficulty,
    ExplanationDepth,
    LearningSignalKind,
    PreferredPace,
    RemediationKind,
    ReviewHorizon,
)
from app.services.language_grammar.enums import GrammarEvidenceSourceSkill

ADAPTIVE_INTELLIGENCE_SCHEMA_VERSION = 1
ADAPTIVE_JSONB_NAMESPACE = "adaptive_intelligence"


@dataclass(frozen=True, slots=True)
class ExplainableReason:
    """One human-readable reason for a recommendation (never black-box)."""

    code: str
    message: str
    weight: float = 1.0


@dataclass(frozen=True, slots=True)
class LearningSignal:
    """Detected weakness / opportunity — does not change curriculum."""

    kind: LearningSignalKind
    grammar_id: str
    severity: float  # 0–100
    reasons: tuple[ExplainableReason, ...] = ()
    display_name: str = ""


@dataclass(frozen=True, slots=True)
class StudentLearningProfile:
    """Persistent preference + derived behavioral profile."""

    student_id: int
    language_id: int
    preferred_pace: PreferredPace = PreferredPace.steady
    preferred_explanation_depth: ExplanationDepth = ExplanationDepth.guided
    preferred_examples: str = "everyday"  # everyday | academic | workplace
    weak_grammar_ids: tuple[str, ...] = ()
    strong_grammar_ids: tuple[str, ...] = ()
    average_confidence: float = 0.0
    average_response_time_seconds: float = 0.0
    retry_frequency: float = 0.0  # 0–1
    preferred_activity_types: tuple[str, ...] = ()
    learning_streak_days: int = 0
    engagement_score: float = 0.0  # 0–100
    schema_version: int = ADAPTIVE_INTELLIGENCE_SCHEMA_VERSION
    curriculum_version: str = ""
    updated_at: str = ""


@dataclass(frozen=True, slots=True)
class TopicConfidenceView:
    """Mastery vs learning confidence for one grammar node."""

    grammar_id: str
    mastery_score: float
    learning_confidence: float
    retention_risk: float
    display_name: str = ""
    state: str = ""


@dataclass(frozen=True, slots=True)
class DifficultyDecision:
    """How hard to teach the current grammar — never changes the target."""

    grammar_id: str
    difficulty_level: AdaptiveDifficulty
    vocabulary_richness: str  # low | medium | high
    sentence_length: str  # short | medium | long
    distractor_quality: str  # soft | balanced | challenging
    reading_complexity: str
    listening_speed: str  # slow | normal | fast
    writing_expectations: str  # supported | standard | extended
    reasons: tuple[ExplainableReason, ...] = ()


@dataclass(frozen=True, slots=True)
class ReviewRecommendation:
    grammar_id: str
    horizon: ReviewHorizon
    urgency: float
    reasons: tuple[ExplainableReason, ...] = ()
    display_name: str = ""
    explanation: str = ""


@dataclass(frozen=True, slots=True)
class ActivityMixWeights:
    """Relative future activity mix — does not unlock grammar."""

    reading: float = 1.0
    listening: float = 1.0
    speaking: float = 1.0
    writing: float = 1.0
    vocabulary: float = 1.0
    reasons: tuple[ExplainableReason, ...] = ()

    def as_dict(self) -> dict[str, float]:
        return {
            "reading": self.reading,
            "listening": self.listening,
            "speaking": self.speaking,
            "writing": self.writing,
            "vocabulary": self.vocabulary,
        }


@dataclass(frozen=True, slots=True)
class RemediationRecommendation:
    grammar_id: str
    kind: RemediationKind
    reasons: tuple[ExplainableReason, ...] = ()
    display_name: str = ""
    explanation: str = ""


@dataclass(frozen=True, slots=True)
class TeacherInsight:
    struggling_topics: tuple[str, ...] = ()
    strength_skills: tuple[str, ...] = ()
    risk_notes: tuple[str, ...] = ()
    focus_grammar_id: str | None = None
    focus_display_name: str = ""
    explanations: tuple[ExplainableReason, ...] = ()


@dataclass(frozen=True, slots=True)
class ParentInsight:
    mastered_percent_band: float = 0.0
    cefr_band: str = ""
    current_focus: str = ""
    current_focus_grammar_id: str | None = None
    recommended_minutes: int = 15
    recommendation_text: str = ""
    explanations: tuple[ExplainableReason, ...] = ()


@dataclass(frozen=True, slots=True)
class AdaptiveIntelligenceBundle:
    """Full adaptive advice for one student × language (read-only)."""

    student_id: int
    language_id: int
    as_of: str
    profile: StudentLearningProfile
    signals: tuple[LearningSignal, ...] = ()
    confidence_views: tuple[TopicConfidenceView, ...] = ()
    difficulty: DifficultyDecision | None = None
    review_recommendations: tuple[ReviewRecommendation, ...] = ()
    activity_mix: ActivityMixWeights = field(default_factory=ActivityMixWeights)
    remediations: tuple[RemediationRecommendation, ...] = ()
    teacher: TeacherInsight = field(default_factory=TeacherInsight)
    parent: ParentInsight = field(default_factory=ParentInsight)
    current_grammar_id: str | None = None
    enabled: bool = True
    schema_version: int = ADAPTIVE_INTELLIGENCE_SCHEMA_VERSION

    def to_student_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "language_id": self.language_id,
            "as_of": self.as_of,
            "current_grammar_id": self.current_grammar_id,
            "difficulty": (
                {
                    "grammar_id": self.difficulty.grammar_id,
                    "difficulty_level": self.difficulty.difficulty_level.value,
                    "vocabulary_richness": self.difficulty.vocabulary_richness,
                    "sentence_length": self.difficulty.sentence_length,
                    "distractor_quality": self.difficulty.distractor_quality,
                    "reading_complexity": self.difficulty.reading_complexity,
                    "listening_speed": self.difficulty.listening_speed,
                    "writing_expectations": self.difficulty.writing_expectations,
                    "reasons": [r.message for r in self.difficulty.reasons],
                }
                if self.difficulty
                else None
            ),
            "review_recommendations": [
                {
                    "grammar_id": r.grammar_id,
                    "display_name": r.display_name,
                    "horizon": r.horizon.value,
                    "urgency": r.urgency,
                    "explanation": r.explanation,
                    "reasons": [x.message for x in r.reasons],
                }
                for r in self.review_recommendations
            ],
            "activity_mix": self.activity_mix.as_dict(),
            "activity_mix_reasons": [r.message for r in self.activity_mix.reasons],
            "remediations": [
                {
                    "grammar_id": m.grammar_id,
                    "kind": m.kind.value,
                    "display_name": m.display_name,
                    "explanation": m.explanation,
                    "reasons": [x.message for x in m.reasons],
                }
                for m in self.remediations
            ],
            "signals": [
                {
                    "kind": s.kind.value,
                    "grammar_id": s.grammar_id,
                    "display_name": s.display_name,
                    "severity": s.severity,
                    "reasons": [x.message for x in s.reasons],
                }
                for s in self.signals
            ],
            "profile": {
                "preferred_pace": self.profile.preferred_pace.value,
                "preferred_explanation_depth": self.profile.preferred_explanation_depth.value,
                "preferred_examples": self.profile.preferred_examples,
                "weak_grammar_ids": list(self.profile.weak_grammar_ids),
                "strong_grammar_ids": list(self.profile.strong_grammar_ids),
                "average_confidence": self.profile.average_confidence,
                "preferred_activity_types": list(self.profile.preferred_activity_types),
                "learning_streak_days": self.profile.learning_streak_days,
                "engagement_score": self.profile.engagement_score,
            },
        }


# Re-export skill enum for activity mix typing convenience
SkillWeightKey = GrammarEvidenceSourceSkill
