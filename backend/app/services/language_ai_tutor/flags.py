"""Feature flags for AI Tutor Foundation (Wave E1)."""

from __future__ import annotations

from app.core.config import get_settings


def ai_tutor_enabled() -> bool:
    settings = get_settings()
    if not bool(getattr(settings, "LANG_GRAMMAR_ENGINE_ENABLED", False)):
        return False
    return bool(getattr(settings, "LANG_AI_TUTOR_ENABLED", False))


def ai_tutor_memory_persist_enabled() -> bool:
    if not ai_tutor_enabled():
        return False
    settings = get_settings()
    return bool(getattr(settings, "LANG_AI_TUTOR_MEMORY_PERSIST", True))


def ai_tutor_llm_enabled() -> bool:
    """When false, always use deterministic template responses."""
    if not ai_tutor_enabled():
        return False
    settings = get_settings()
    return bool(getattr(settings, "LANG_AI_TUTOR_LLM_ENABLED", True))
