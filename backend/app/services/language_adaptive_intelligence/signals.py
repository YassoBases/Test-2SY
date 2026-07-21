"""Weakness detection — learning signals only; no curriculum changes."""

from __future__ import annotations

from app.services.language_adaptive_intelligence.confidence import (
    days_since,
    learning_confidence_for_record,
)
from app.services.language_adaptive_intelligence.enums import LearningSignalKind
from app.services.language_adaptive_intelligence.types import ExplainableReason, LearningSignal
from app.services.language_grammar_catalog.catalog import get_topic
from app.services.language_grammar_mastery.types import GrammarMasterySnapshot


def detect_learning_signals(
    mastery: GrammarMasterySnapshot,
    *,
    as_of: str,
    max_signals: int = 12,
) -> tuple[LearningSignal, ...]:
    """Deterministically emit weakness / opportunity signals from mastery snapshot."""
    signals: list[LearningSignal] = []
    for rec in mastery.records:
        topic = get_topic(rec.grammar_id)
        name = topic.display_name if topic else rec.grammar_id
        conf = learning_confidence_for_record(rec, as_of=as_of)
        mastery_score = float(rec.dimensions.overall_mastery)
        idle = days_since(as_of, rec.last_seen_at)
        accuracy = float(rec.dimensions.accuracy)

        if conf < 45.0 and mastery_score >= 55.0:
            signals.append(
                LearningSignal(
                    kind=LearningSignalKind.low_confidence,
                    grammar_id=rec.grammar_id,
                    display_name=name,
                    severity=round(100.0 - conf, 2),
                    reasons=(
                        ExplainableReason(
                            code="low_confidence",
                            message=f"Learning confidence is {conf:.0f}% despite mastery {mastery_score:.0f}%",
                            weight=1.2,
                        ),
                    ),
                )
            )

        if float(rec.retention_risk) >= 0.55:
            signals.append(
                LearningSignal(
                    kind=LearningSignalKind.retention_risk,
                    grammar_id=rec.grammar_id,
                    display_name=name,
                    severity=round(float(rec.retention_risk) * 100.0, 2),
                    reasons=(
                        ExplainableReason(
                            code="retention_risk",
                            message=f"Retention risk is elevated ({rec.retention_risk:.2f})",
                            weight=1.3,
                        ),
                    ),
                )
            )

        if idle is not None and idle >= 9 and mastery_score >= 40.0:
            signals.append(
                LearningSignal(
                    kind=LearningSignalKind.long_inactivity
                    if idle < 21
                    else LearningSignalKind.forgotten_grammar,
                    grammar_id=rec.grammar_id,
                    display_name=name,
                    severity=min(100.0, round(idle * 4.0, 2)),
                    reasons=(
                        ExplainableReason(
                            code="inactivity",
                            message=f"Last practice was {idle:.0f} days ago",
                            weight=1.1,
                        ),
                    ),
                )
            )

        if accuracy < 55.0 and rec.evidence_count >= 3:
            signals.append(
                LearningSignal(
                    kind=LearningSignalKind.recurring_mistakes,
                    grammar_id=rec.grammar_id,
                    display_name=name,
                    severity=round(100.0 - accuracy, 2),
                    reasons=(
                        ExplainableReason(
                            code="low_accuracy",
                            message=f"Accuracy remains low ({accuracy:.0f}%) across {rec.evidence_count} observations",
                            weight=1.4,
                        ),
                    ),
                )
            )

        if rec.stability < 0.35 and rec.evidence_count >= 3:
            signals.append(
                LearningSignal(
                    kind=LearningSignalKind.unstable_performance,
                    grammar_id=rec.grammar_id,
                    display_name=name,
                    severity=round((1.0 - float(rec.stability)) * 100.0, 2),
                    reasons=(
                        ExplainableReason(
                            code="unstable",
                            message=f"Performance stability is low ({rec.stability:.2f})",
                            weight=1.0,
                        ),
                    ),
                )
            )

        if len(rec.skill_coverage) <= 1 and rec.evidence_count >= 2:
            missing = "cross-skill practice"
            signals.append(
                LearningSignal(
                    kind=LearningSignalKind.skill_gap,
                    grammar_id=rec.grammar_id,
                    display_name=name,
                    severity=40.0,
                    reasons=(
                        ExplainableReason(
                            code="skill_gap",
                            message=f"Evidence is concentrated in few skills; needs more {missing}",
                            weight=0.8,
                        ),
                    ),
                )
            )

        if rec.evidence_count >= 4 and accuracy < 70.0 and conf < 50.0:
            signals.append(
                LearningSignal(
                    kind=LearningSignalKind.repeated_retries,
                    grammar_id=rec.grammar_id,
                    display_name=name,
                    severity=round((100.0 - accuracy + (50.0 - conf)) / 2.0, 2),
                    reasons=(
                        ExplainableReason(
                            code="retries",
                            message="Multiple attempts without stable accuracy suggest repeated retries",
                            weight=1.0,
                        ),
                    ),
                )
            )

    signals.sort(key=lambda s: (-s.severity, s.kind.value, s.grammar_id))
    # Deduplicate by (kind, grammar_id) keeping highest severity
    seen: set[tuple[str, str]] = set()
    unique: list[LearningSignal] = []
    for sig in signals:
        key = (sig.kind.value, sig.grammar_id)
        if key in seen:
            continue
        seen.add(key)
        unique.append(sig)
        if len(unique) >= max_signals:
            break
    return tuple(unique)
