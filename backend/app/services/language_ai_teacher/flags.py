"""Feature flags for Autonomous AI Teacher (Phase F)."""

from __future__ import annotations

from app.core.config import get_settings


def ai_teacher_enabled() -> bool:
    settings = get_settings()
    if not bool(getattr(settings, "LANG_GRAMMAR_ENGINE_ENABLED", False)):
        return False
    return bool(getattr(settings, "LANG_AI_TEACHER_ENABLED", False))


def ai_teacher_persist_enabled() -> bool:
    if not ai_teacher_enabled():
        return False
    settings = get_settings()
    return bool(getattr(settings, "LANG_AI_TEACHER_PERSIST", True))
