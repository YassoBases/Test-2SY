"""Feature flags for Adaptive Learning Intelligence (Phase 2)."""

from __future__ import annotations

from app.core.config import get_settings


def adaptive_intelligence_enabled() -> bool:
    """Adaptive advice layer — independent of curriculum / mastery writes."""
    settings = get_settings()
    # Requires grammar engine readable data; own flag defaults off.
    if not bool(getattr(settings, "LANG_GRAMMAR_ENGINE_ENABLED", False)):
        return False
    return bool(getattr(settings, "LANG_ADAPTIVE_INTELLIGENCE_ENABLED", False))


def adaptive_profile_persist_enabled() -> bool:
    """Optional persistence of derived learning profile (adaptive namespace only)."""
    if not adaptive_intelligence_enabled():
        return False
    settings = get_settings()
    return bool(getattr(settings, "LANG_ADAPTIVE_PROFILE_PERSIST", True))
