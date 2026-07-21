"""Review, activity-mix, and remediation recommendations — explainable & deterministic."""

from __future__ import annotations

from app.services.language_adaptive_intelligence.confidence import (
    days_since,
    learning_confidence_for_record,
)
from app.services.language_adaptive_intelligence.enums import (
    RemediationKind,
    ReviewHorizon,
)
from app.services.language_adaptive_intelligence.types import (
    ActivityMixWeights,
    ExplainableReason,
    LearningSignal,
    RemediationRecommendation,
    ReviewRecommendation,
)
from app.services.language_grammar_catalog.catalog import get_topic
from app.services.language_grammar_mastery.types import GrammarMasterySnapshot
from app.services.language_grammar_review.types import GrammarReviewSnapshot


def _horizon_for(urgency: float, idle_days: float | None) -> ReviewHorizon:
    if urgency >= 70.0 or (idle_days is not None and idle_days >= 9):
        return ReviewHorizon.today
    if urgency >= 45.0 or (idle_days is not None and idle_days >= 5):
        return ReviewHorizon.tomorrow
    if urgency >= 25.0:
        return ReviewHorizon.this_week
    return ReviewHorizon.later


def build_review_recommendations(
    mastery: GrammarMasterySnapshot,
    *,
    as_of: str,
    review: GrammarReviewSnapshot | None = None,
    max_items: int = 8,
) -> tuple[ReviewRecommendation, ...]:
    """Recommend review timing — never unlocks grammar."""
    due_ids = {item.grammar_id for item in (review.queue.items if review else ())}
    rows: list[ReviewRecommendation] = []
    for rec in mastery.records:
        if rec.evidence_count <= 0:
            continue
        conf = learning_confidence_for_record(rec, as_of=as_of)
        idle = days_since(as_of, rec.last_seen_at)
        urgency = 0.0
        reasons: list[ExplainableReason] = []

        if rec.grammar_id in due_ids:
            urgency += 35.0
            reasons.append(
                ExplainableReason(
                    code="review_due",
                    message="Already due on the grammar review schedule",
                    weight=1.2,
                )
            )
        if conf < 50.0:
            urgency += (50.0 - conf) * 0.8
            reasons.append(
                ExplainableReason(
                    code="confidence_dropped",
                    message=f"Confidence dropped to {conf:.0f}%",
                    weight=1.3,
                )
            )
        if float(rec.dimensions.accuracy) < 65.0 and rec.evidence_count >= 2:
            urgency += 20.0
            reasons.append(
                ExplainableReason(
                    code="recent_mistakes",
                    message=f"Accuracy is {rec.dimensions.accuracy:.0f}% across recent evidence",
                    weight=1.2,
                )
            )
        if idle is not None and idle >= 7:
            urgency += min(30.0, idle * 2.0)
            reasons.append(
                ExplainableReason(
                    code="days_since_practice",
                    message=f"Last practice {idle:.0f} days ago",
                    weight=1.1,
                )
            )
        if float(rec.retention_risk) >= 0.5:
            urgency += float(rec.retention_risk) * 20.0
            reasons.append(
                ExplainableReason(
                    code="retention_risk",
                    message=f"Retention risk {rec.retention_risk:.2f}",
                    weight=1.0,
                )
            )

        if urgency < 15.0 and not reasons:
            continue

        urgency = min(100.0, round(urgency, 2))
        horizon = _horizon_for(urgency, idle)
        topic = get_topic(rec.grammar_id)
        name = topic.display_name if topic else rec.grammar_id
        explanation = (
            f"We recommend reviewing {name} because:\n"
            + "\n".join(f"• {r.message}" for r in reasons)
        )
        rows.append(
            ReviewRecommendation(
                grammar_id=rec.grammar_id,
                display_name=name,
                horizon=horizon,
                urgency=urgency,
                reasons=tuple(reasons),
                explanation=explanation,
            )
        )

    rows.sort(key=lambda r: (-r.urgency, r.grammar_id))
    return tuple(rows[:max_items])


def build_activity_mix(
    mastery: GrammarMasterySnapshot,
    *,
    as_of: str,
    current_grammar_id: str | None,
) -> ActivityMixWeights:
    """Increase under-practiced skills for the current grammar; progression unchanged."""
    weights = {
        "reading": 1.0,
        "listening": 1.0,
        "speaking": 1.0,
        "writing": 1.0,
        "vocabulary": 0.8,
    }
    reasons: list[ExplainableReason] = []
    rec = mastery.record_for(current_grammar_id) if current_grammar_id else None
    if rec is None:
        return ActivityMixWeights(reasons=(ExplainableReason(
            code="default_mix",
            message="No current grammar focus — using balanced activity mix",
        ),))

    covered = {s.value if hasattr(s, "value") else str(s) for s in rec.skill_coverage}
    for skill in ("reading", "listening", "speaking", "writing"):
        if skill not in covered:
            weights[skill] = 1.45
            reasons.append(
                ExplainableReason(
                    code=f"boost_{skill}",
                    message=f"Little {skill} evidence on current grammar — increase {skill} frequency",
                    weight=1.0,
                )
            )
        else:
            weights[skill] = 0.85

    # If accuracy low on speaking-heavy coverage, boost speaking further
    if float(rec.dimensions.accuracy) < 60.0:
        weights["speaking"] = max(weights["speaking"], 1.5)
        weights["writing"] = max(weights["writing"], 1.35)
        reasons.append(
            ExplainableReason(
                code="production_support",
                message="Accuracy is still weak — prioritize speaking and writing practice",
                weight=1.2,
            )
        )

    conf = learning_confidence_for_record(rec, as_of=as_of)
    if conf < 45.0:
        weights["vocabulary"] = 1.1
        reasons.append(
            ExplainableReason(
                code="vocab_support",
                message="Low confidence — add light vocabulary support aligned to grammar",
                weight=0.8,
            )
        )

    if not reasons:
        reasons.append(
            ExplainableReason(
                code="balanced_mix",
                message="Skill coverage is balanced — keep an even activity mix",
            )
        )

    return ActivityMixWeights(
        reading=round(weights["reading"], 2),
        listening=round(weights["listening"], 2),
        speaking=round(weights["speaking"], 2),
        writing=round(weights["writing"], 2),
        vocabulary=round(weights["vocabulary"], 2),
        reasons=tuple(reasons),
    )


def build_remediations(
    signals: tuple[LearningSignal, ...],
    mastery: GrammarMasterySnapshot,
    *,
    as_of: str,
    max_items: int = 6,
) -> tuple[RemediationRecommendation, ...]:
    """Recommend remediation supports — never unlocks or downgrades grammar."""
    out: list[RemediationRecommendation] = []
    for sig in signals:
        rec = mastery.record_for(sig.grammar_id)
        if rec is None:
            continue
        topic = get_topic(sig.grammar_id)
        name = topic.display_name if topic else sig.grammar_id
        kind = RemediationKind.grammar_recap
        if sig.kind.value == "recurring_mistakes":
            kind = RemediationKind.additional_examples
        elif sig.kind.value == "low_confidence":
            kind = RemediationKind.easier_explanation
        elif sig.kind.value in {"forgotten_grammar", "long_inactivity"}:
            kind = RemediationKind.mini_lesson
        elif sig.kind.value == "skill_gap":
            kind = RemediationKind.vocabulary_support

        reasons = list(sig.reasons) + [
            ExplainableReason(
                code="remediation",
                message=f"Recommend {kind.value.replace('_', ' ')} for {name}",
                weight=1.0,
            )
        ]
        explanation = (
            f"Recommend {kind.value.replace('_', ' ')} for {name} because:\n"
            + "\n".join(f"• {r.message}" for r in sig.reasons)
        )
        out.append(
            RemediationRecommendation(
                grammar_id=sig.grammar_id,
                kind=kind,
                display_name=name,
                reasons=tuple(reasons),
                explanation=explanation,
            )
        )
        if len(out) >= max_items:
            break
    return tuple(out)
