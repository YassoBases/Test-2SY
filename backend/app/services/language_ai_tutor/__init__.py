"""AI Tutor Foundation (Wave E1).

RESPONSIBILITY: Orchestration / communication layer over Grammar Engine + Adaptive
Intelligence. Explains, hints, motivates, summarizes — never chooses grammar,
never writes mastery/progression/evidence/curriculum/adaptive profile.
Conversation memory may be persisted under ai_tutor JSONB only.
"""

from __future__ import annotations

from app.services.language_ai_tutor.flags import (
    ai_tutor_enabled,
    ai_tutor_llm_enabled,
    ai_tutor_memory_persist_enabled,
)
from app.services.language_ai_tutor.service import (
    build_tutor_context_async,
    build_tutor_context_pure,
    respond_tutor_turn,
)
from app.services.language_ai_tutor.types import (
    AI_TUTOR_JSONB_NAMESPACE,
    AI_TUTOR_PACKAGE,
    AI_TUTOR_SCHEMA_VERSION,
    ConversationMemory,
    TutorContext,
    TutorResponse,
    TutorTurnRequest,
)

PACKAGE_VERSION = "1.0.0"
RESPONSIBILITY = (
    "AI Tutor Foundation — Tutor Context, Prompt Orchestrator, Conversation Memory, "
    "Teacher Persona, adaptive explanation style; read-only over educational engines"
)

__all__ = [
    "PACKAGE_VERSION",
    "RESPONSIBILITY",
    "AI_TUTOR_SCHEMA_VERSION",
    "AI_TUTOR_JSONB_NAMESPACE",
    "AI_TUTOR_PACKAGE",
    "ConversationMemory",
    "TutorContext",
    "TutorResponse",
    "TutorTurnRequest",
    "ai_tutor_enabled",
    "ai_tutor_llm_enabled",
    "ai_tutor_memory_persist_enabled",
    "build_tutor_context_async",
    "build_tutor_context_pure",
    "respond_tutor_turn",
]
