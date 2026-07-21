"""Learning journey — read-only visible progress; never mutates engines."""

from __future__ import annotations

from app.services.language_adaptive_intelligence.types import AdaptiveIntelligenceBundle
from app.services.language_ai_teacher.types import ExplainableNote, LearningJourney, LearningMission
from app.services.language_grammar.enums import GrammarMasteryState
from app.services.language_grammar_catalog.catalog import get_default_catalog, get_topic
from app.services.language_grammar_mastery.types import GrammarMasterySnapshot
from app.services.language_grammar_progression.types import GrammarProgressionSnapshot


def build_learning_journey(
    *,
    mastery: GrammarMasterySnapshot | None,
    progression: GrammarProgressionSnapshot | None,
    adaptive: AdaptiveIntelligenceBundle | None,
    mission: LearningMission | None,
) -> LearningJourney:
    catalog = get_default_catalog()
    total = len(catalog.topics)
    completed = 0
    if mastery:
        completed = sum(1 for r in mastery.records if r.state is GrammarMasteryState.mastered)

    current_id = progression.current_grammar_id if progression else None
    current_name = ""
    if current_id:
        topic = get_topic(current_id)
        current_name = topic.display_name if topic else current_id

    upcoming = ""
    if progression and progression.next_grammar_id:
        nxt = get_topic(progression.next_grammar_id)
        upcoming = nxt.display_name if nxt else progression.next_grammar_id

    conf = adaptive.profile.average_confidence if adaptive and adaptive.enabled else 0.0
    if conf >= 70.0:
        trend = "rising"
    elif conf < 45.0:
        trend = "soft"
    else:
        trend = "steady"

    streak = int(adaptive.profile.learning_streak_days) if adaptive and adaptive.enabled else 0
    progress = 0.0
    if total:
        progress = round(100.0 * completed / total, 1)

    return LearningJourney(
        current_mission=mission.title if mission else "",
        todays_progress_percent=progress,
        grammar_completed_count=completed,
        grammar_total_count=total,
        current_grammar_id=current_id,
        current_grammar_name=current_name,
        confidence_trend=trend,
        weekly_streak_days=streak,
        upcoming_lesson=upcoming,
        reasons=(
            ExplainableNote(
                code="journey_readonly",
                message="Journey is a read-only projection of mastery/progression/adaptive signals.",
            ),
        ),
    )
