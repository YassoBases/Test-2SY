"""Autonomous AI Teacher (Phase F).

RESPONSIBILITY: Orchestrate today's learning session (goals, review, activity order,
missions, weekly plan, journey, wrap-up) ABOVE locked Grammar / Adaptive / Tutor /
Coaching layers. Never writes mastery, progression, unlocks, curriculum, adaptive,
or tutor/coaching educational state. May persist generated sessions under ai_teacher.
"""

from __future__ import annotations

from app.services.language_ai_teacher.flags import (
    ai_teacher_enabled,
    ai_teacher_persist_enabled,
)
from app.services.language_ai_teacher.service import (
    build_learning_session_pure,
    start_learning_session,
)
from app.services.language_ai_teacher.types import (
    AI_TEACHER_JSONB_NAMESPACE,
    AI_TEACHER_PACKAGE,
    AI_TEACHER_SCHEMA_VERSION,
    LearningSession,
)

PACKAGE_VERSION = "1.0.0"
RESPONSIBILITY = (
    "Autonomous AI Teacher — session orchestrator for today's teaching flow; "
    "read-only over Grammar Engine, Adaptive Intelligence, Tutor, and Coaching"
)

__all__ = [
    "PACKAGE_VERSION",
    "RESPONSIBILITY",
    "AI_TEACHER_SCHEMA_VERSION",
    "AI_TEACHER_JSONB_NAMESPACE",
    "AI_TEACHER_PACKAGE",
    "LearningSession",
    "ai_teacher_enabled",
    "ai_teacher_persist_enabled",
    "start_learning_session",
    "build_learning_session_pure",
]
