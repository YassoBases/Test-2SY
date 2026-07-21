"""Conversational Coaching (Wave E2).

RESPONSIBILITY: Socratic tutoring, multi-level hints, mistake diagnosis, reflection,
motivation, and lesson wrap-up on top of locked AI Tutor Foundation.
Never writes mastery/progression/evidence/curriculum/adaptive profile.
May persist coaching session state under ai_tutor_coaching JSONB only.
"""

from __future__ import annotations

from app.services.language_ai_tutor_coaching.flags import (
    coaching_llm_enabled,
    coaching_state_persist_enabled,
    conversational_coaching_enabled,
)
from app.services.language_ai_tutor_coaching.service import (
    build_coaching_context_pure,
    respond_coaching_turn,
    respond_coaching_turn_pure,
)
from app.services.language_ai_tutor_coaching.types import (
    COACHING_JSONB_NAMESPACE,
    COACHING_PACKAGE,
    COACHING_SCHEMA_VERSION,
    CoachingTurnRequest,
    CoachingTurnResponse,
)

PACKAGE_VERSION = "1.0.0"
RESPONSIBILITY = (
    "Conversational Coaching — Socratic guidance, hint ladder, diagnosis, reflection, "
    "motivation, wrap-up; extends AI Tutor Foundation without becoming educational authority"
)

__all__ = [
    "PACKAGE_VERSION",
    "RESPONSIBILITY",
    "COACHING_SCHEMA_VERSION",
    "COACHING_JSONB_NAMESPACE",
    "COACHING_PACKAGE",
    "CoachingTurnRequest",
    "CoachingTurnResponse",
    "conversational_coaching_enabled",
    "coaching_state_persist_enabled",
    "coaching_llm_enabled",
    "respond_coaching_turn",
    "respond_coaching_turn_pure",
    "build_coaching_context_pure",
]
