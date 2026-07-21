"""Weekly learning planner — adaptive signals only; informational."""

from __future__ import annotations

from app.services.language_adaptive_intelligence.types import AdaptiveIntelligenceBundle
from app.services.language_ai_teacher.enums import Weekday
from app.services.language_ai_teacher.types import ExplainableNote, WeeklyDayPlan, WeeklyPlan


_BASE_WEEK: tuple[tuple[Weekday, str, tuple[str, ...]], ...] = (
    (Weekday.monday, "Reading", ("reading", "vocabulary")),
    (Weekday.tuesday, "Speaking", ("speaking", "listening")),
    (Weekday.wednesday, "Grammar Review", ("grammar", "quiz")),
    (Weekday.thursday, "Writing", ("writing", "grammar")),
    (Weekday.friday, "Quiz", ("quiz", "speaking")),
    (Weekday.saturday, "Revision", ("review", "reading")),
    (Weekday.sunday, "Rest", ()),
)


def generate_weekly_plan(
    *,
    student_id: int,
    language_id: int,
    adaptive: AdaptiveIntelligenceBundle | None,
    as_of: str,
) -> WeeklyPlan:
    days: list[WeeklyDayPlan] = []
    reasons: list[ExplainableNote] = [
        ExplainableNote(
            code="base_week",
            message="Starting from a balanced weekly template.",
        )
    ]
    boost = "speaking"
    if adaptive and adaptive.enabled:
        mix = adaptive.activity_mix.as_dict()
        boost = max(("reading", "listening", "speaking", "writing"), key=lambda k: mix.get(k, 1.0))
        reasons.append(
            ExplainableNote(
                code="adaptive_boost",
                message=f"Adaptive mix prioritizes {boost} — elevate it mid-week.",
            )
        )
        if adaptive.review_recommendations:
            reasons.append(
                ExplainableNote(
                    code="review_slot",
                    message="Adaptive review items exist — keep Wednesday as grammar review.",
                )
            )

    for day, focus, kinds in _BASE_WEEK:
        notes = ""
        kinds_list = list(kinds)
        if day is Weekday.tuesday and boost != "speaking":
            focus = boost.title()
            kinds_list = [boost, "listening"] if boost != "listening" else ["listening", "speaking"]
            notes = f"Adjusted from adaptive priority: {boost}."
        if day is Weekday.sunday:
            notes = "Rest day — no unlock or mastery changes."
        days.append(
            WeeklyDayPlan(
                day=day,
                focus=focus,
                activity_kinds=tuple(kinds_list),
                notes=notes,
            )
        )

    return WeeklyPlan(
        student_id=student_id,
        language_id=language_id,
        days=tuple(days),
        reasons=tuple(reasons),
        as_of=as_of,
    )
