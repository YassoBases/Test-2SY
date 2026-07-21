"""Learning mission generator — every mission maps to an existing grammar target."""

from __future__ import annotations

from app.services.language_ai_teacher.types import ExplainableNote, LearningMission
from app.services.language_grammar_catalog.catalog import get_topic

# Deterministic scenario templates keyed by grammar_id substrings / exact ids.
_MISSION_BY_GRAMMAR: dict[str, tuple[str, str]] = {
    "gram_present_simple": ("Introduce yourself", "Introduce yourself to a new classmate."),
    "gram_present_continuous": ("Describe what is happening", "Describe what people are doing right now."),
    "gram_past_simple": ("Describe your weekend", "Tell a friend what you did last weekend."),
    "gram_present_perfect": ("Talk about life experience", "Share experiences using present perfect."),
    "gram_present_perfect_continuous": (
        "Talk about ongoing activities",
        "Explain activities that started in the past and continue now.",
    ),
    "gram_future_forms": ("Talk about future plans", "Discuss your plans for next week."),
    "gram_going_to_future": ("Talk about future plans", "Share intentions using going to."),
    "gram_will_future": ("Make predictions", "Make polite predictions about the weekend."),
    "gram_first_conditional": ("Travel decisions", "Decide what to do if your flight is delayed."),
    "gram_second_conditional": ("Imagine a trip", "Imagine what you would do on a dream trip."),
    "gram_modals_ability": ("Order food in English", "Order food politely at a cafe."),
    "gram_modals_permission": ("Ask for help politely", "Ask for permission and help at school."),
    "gram_passive_voice": ("Describe a process", "Explain how something is made or done."),
    "gram_relative_clauses": ("Describe people and places", "Describe people and places with relative clauses."),
}

_DEFAULT_MISSION = ("Practice today's grammar in a real situation", "Use today's grammar in a short real-life dialogue.")


def mission_for_grammar(grammar_id: str | None) -> LearningMission | None:
    if not grammar_id:
        return None
    topic = get_topic(grammar_id)
    name = topic.display_name if topic else grammar_id
    title, scenario = _MISSION_BY_GRAMMAR.get(grammar_id, _DEFAULT_MISSION)
    # Soft match for related ids
    if grammar_id not in _MISSION_BY_GRAMMAR:
        for key, pair in _MISSION_BY_GRAMMAR.items():
            if key in grammar_id or grammar_id in key:
                title, scenario = pair
                break
    return LearningMission(
        mission_id=f"mission_{grammar_id}",
        title=title,
        scenario=scenario,
        grammar_id=grammar_id,
        grammar_display_name=name,
        reasons=(
            ExplainableNote(
                code="grammar_mapped",
                message=f"Mission maps to existing grammar target {grammar_id} ({name}).",
            ),
        ),
    )
