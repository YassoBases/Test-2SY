"""Teacher Persona integration — reuse authoring TeacherPersona; configurable traits."""

from __future__ import annotations

from app.services.language_grammar_activity_authoring.types import TeacherPersona

# Stable trait vocabulary for configurable personas (future teachers reuse this).
DEFAULT_PERSONA_TRAITS: tuple[str, ...] = (
    "supportive",
    "patient",
    "encouraging",
    "clear",
    "professional",
    "age_appropriate",
)

PERSONA_CATALOG: dict[str, TeacherPersona] = {
    "default_tutor": TeacherPersona(
        persona_id="default_tutor",
        tone="supportive",
        extras={
            "traits": ",".join(DEFAULT_PERSONA_TRAITS),
            "style": "warm_professional",
            "contradict_prior": "false",
        },
    ),
    "encouraging_coach": TeacherPersona(
        persona_id="encouraging_coach",
        tone="encouraging",
        extras={
            "traits": "supportive,encouraging,clear,age_appropriate",
            "style": "motivational",
            "contradict_prior": "false",
        },
    ),
    "calm_guide": TeacherPersona(
        persona_id="calm_guide",
        tone="patient",
        extras={
            "traits": "patient,clear,professional,age_appropriate",
            "style": "calm_guided",
            "contradict_prior": "false",
        },
    ),
}


def resolve_teacher_persona(
    persona: TeacherPersona | None = None,
    *,
    persona_id: str | None = None,
) -> TeacherPersona:
    """Resolve configurable persona; never invent curriculum voice rules."""
    if persona is not None:
        extras = dict(persona.extras)
        if "traits" not in extras:
            extras["traits"] = ",".join(DEFAULT_PERSONA_TRAITS)
        if "contradict_prior" not in extras:
            extras["contradict_prior"] = "false"
        return TeacherPersona(
            persona_id=persona.persona_id or "default_tutor",
            tone=persona.tone or "supportive",
            extras=extras,
        )
    key = (persona_id or "default_tutor").strip() or "default_tutor"
    return PERSONA_CATALOG.get(key, PERSONA_CATALOG["default_tutor"])


def persona_system_lines(persona: TeacherPersona) -> list[str]:
    traits = persona.extras.get("traits") or ",".join(DEFAULT_PERSONA_TRAITS)
    return [
        f"You are the student's assigned AI teacher (persona_id={persona.persona_id}).",
        f"Tone: {persona.tone}.",
        f"Traits: {traits.replace(',', ', ')}.",
        "Sound like this teacher consistently; do not invent a different persona.",
        "Never contradict previous explanations unless curriculum context changes.",
        "Stay age-appropriate and professional.",
    ]
