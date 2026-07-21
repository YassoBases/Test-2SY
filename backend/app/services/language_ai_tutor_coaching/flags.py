"""Feature flags for Conversational Coaching (Wave E2)."""

from __future__ import annotations

from app.core.config import get_settings
from app.services.language_ai_tutor.flags import ai_tutor_enabled


def conversational_coaching_enabled() -> bool:
    """Requires AI Tutor Foundation; own flag defaults off."""
    if not ai_tutor_enabled():
        return False
    settings = get_settings()
    return bool(getattr(settings, "LANG_AI_TUTOR_COACHING_ENABLED", False))


def coaching_state_persist_enabled() -> bool:
    if not conversational_coaching_enabled():
        return False
    settings = get_settings()
    return bool(getattr(settings, "LANG_AI_TUTOR_COACHING_PERSIST", True))


def coaching_llm_enabled() -> bool:
    if not conversational_coaching_enabled():
        return False
    settings = get_settings()
    return bool(getattr(settings, "LANG_AI_TUTOR_COACHING_LLM_ENABLED", True))
