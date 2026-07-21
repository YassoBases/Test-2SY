"""Daily goal generator — derived only from existing educational state."""

from __future__ import annotations

from app.services.language_adaptive_intelligence.types import AdaptiveIntelligenceBundle
from app.services.language_ai_teacher.types import DailyGoal, ExplainableNote
from app.services.language_grammar_catalog.catalog import get_topic
from app.services.language_grammar_progression.types import GrammarProgressionSnapshot


def generate_daily_goals(
    *,
    progression: GrammarProgressionSnapshot | None,
    adaptive: AdaptiveIntelligenceBundle | None,
    max_goals: int = 4,
) -> tuple[DailyGoal, ...]:
    goals: list[DailyGoal] = []
    current_id = progression.current_grammar_id if progression else None
    if current_id:
        topic = get_topic(current_id)
        name = topic.display_name if topic else current_id
        goals.append(
            DailyGoal(
                goal_id=f"goal_master_{current_id}",
                title=f"Master {name}",
                source="grammar",
                grammar_id=current_id,
                reasons=(
                    ExplainableNote(
                        code="current_grammar",
                        message=f"Current grammar focus from progression is {name}.",
                    ),
                ),
            )
        )

    if adaptive and adaptive.enabled:
        mix = adaptive.activity_mix.as_dict()
        weak_skill = max(mix.items(), key=lambda kv: kv[1])[0] if mix else None
        if weak_skill and weak_skill == "speaking" and mix.get("speaking", 1.0) >= 1.2:
            goals.append(
                DailyGoal(
                    goal_id="goal_speaking_confidence",
                    title="Improve Speaking Confidence",
                    source="adaptive",
                    skill="speaking",
                    reasons=(
                        ExplainableNote(
                            code="activity_mix",
                            message="Adaptive mix boosts speaking — prioritize spoken practice today.",
                        ),
                    ),
                )
            )
        for gid in adaptive.profile.weak_grammar_ids[:2]:
            if gid == current_id:
                continue
            topic = get_topic(gid)
            name = topic.display_name if topic else gid
            goals.append(
                DailyGoal(
                    goal_id=f"goal_review_{gid}",
                    title=f"Review {name}",
                    source="review",
                    grammar_id=gid,
                    reasons=(
                        ExplainableNote(
                            code="weak_profile",
                            message=f"{name} appears in the learning profile weak list.",
                        ),
                    ),
                )
            )
            break
        if mix.get("reading", 1.0) >= 1.2:
            goals.append(
                DailyGoal(
                    goal_id="goal_reading_practice",
                    title="Complete Reading Practice",
                    source="skill",
                    skill="reading",
                    reasons=(
                        ExplainableNote(
                            code="reading_boost",
                            message="Adaptive activity mix recommends more reading practice.",
                        ),
                    ),
                )
            )

    # Deduplicate by goal_id
    seen: set[str] = set()
    unique: list[DailyGoal] = []
    for g in goals:
        if g.goal_id in seen:
            continue
        seen.add(g.goal_id)
        unique.append(g)
        if len(unique) >= max_goals:
            break
    return tuple(unique)
