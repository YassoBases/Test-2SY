"""Learning confidence model — advisory only; never writes mastery."""

from __future__ import annotations

from datetime import datetime, timezone

from app.services.language_adaptive_intelligence.types import TopicConfidenceView
from app.services.language_grammar_catalog.catalog import get_topic
from app.services.language_grammar_mastery.types import GrammarMasteryRecord, GrammarMasterySnapshot


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def days_since(as_of: str, last_seen: str | None) -> float | None:
    end = _parse_ts(as_of) or datetime.now(timezone.utc)
    start = _parse_ts(last_seen)
    if start is None:
        return None
    return max(0.0, (end - start).total_seconds() / 86400.0)


def learning_confidence_for_record(
    record: GrammarMasteryRecord,
    *,
    as_of: str,
) -> float:
    """Derive learning_confidence 0–100 from mastery record signals.

    High mastery + stale practice / high retention risk → lower confidence.
    Deterministic; no RNG.
    """
    base = max(0.0, min(100.0, float(record.confidence) * 100.0))
    if base <= 0.0 and record.evidence_count > 0:
        base = max(20.0, float(record.dimensions.overall_mastery) * 0.6)

    idle = days_since(as_of, record.last_seen_at)
    if idle is not None:
        if idle >= 14:
            base -= min(35.0, (idle - 13) * 2.5)
        elif idle >= 7:
            base -= min(20.0, (idle - 6) * 2.0)

    base -= max(0.0, min(25.0, float(record.retention_risk) * 25.0))
    if record.stability < 0.4 and record.evidence_count >= 2:
        base -= 10.0
    if record.evidence_count < 2:
        base -= 8.0

    return max(0.0, min(100.0, round(base, 2)))


def build_confidence_views(
    mastery: GrammarMasterySnapshot,
    *,
    as_of: str,
) -> tuple[TopicConfidenceView, ...]:
    views: list[TopicConfidenceView] = []
    for rec in mastery.records:
        topic = get_topic(rec.grammar_id)
        views.append(
            TopicConfidenceView(
                grammar_id=rec.grammar_id,
                mastery_score=float(rec.dimensions.overall_mastery),
                learning_confidence=learning_confidence_for_record(rec, as_of=as_of),
                retention_risk=float(rec.retention_risk),
                display_name=topic.display_name if topic else rec.grammar_id,
                state=rec.state.value if hasattr(rec.state, "value") else str(rec.state),
            )
        )
    views.sort(key=lambda v: (-(100.0 - v.learning_confidence), -v.retention_risk, v.grammar_id))
    return tuple(views)
