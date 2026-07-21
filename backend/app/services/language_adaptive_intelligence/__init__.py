"""Adaptive Learning Intelligence (Phase 2).

RESPONSIBILITY: Read-only personalization layer — decides HOW to teach from
mastery/progression/review signals; never changes WHAT the curriculum is.
Never writes mastery, progression unlocks, resolver targets, or curriculum.
"""

from __future__ import annotations

from app.services.language_adaptive_intelligence.flags import (
    adaptive_intelligence_enabled,
    adaptive_profile_persist_enabled,
)
from app.services.language_adaptive_intelligence.service import (
    build_adaptive_bundle,
    build_adaptive_bundle_async,
    empty_adaptive_bundle,
)
from app.services.language_adaptive_intelligence.types import (
    ADAPTIVE_INTELLIGENCE_SCHEMA_VERSION,
    ADAPTIVE_JSONB_NAMESPACE,
    AdaptiveIntelligenceBundle,
    StudentLearningProfile,
)

PACKAGE_VERSION = "1.0.0"
RESPONSIBILITY = (
    "Adaptive Learning Intelligence — profile, weakness signals, difficulty, "
    "review recommendations, activity mix, remediation, confidence, "
    "teacher/parent insights; read-only over Grammar Engine v1.0"
)

__all__ = [
    "PACKAGE_VERSION",
    "RESPONSIBILITY",
    "ADAPTIVE_INTELLIGENCE_SCHEMA_VERSION",
    "ADAPTIVE_JSONB_NAMESPACE",
    "AdaptiveIntelligenceBundle",
    "StudentLearningProfile",
    "adaptive_intelligence_enabled",
    "adaptive_profile_persist_enabled",
    "build_adaptive_bundle",
    "build_adaptive_bundle_async",
    "empty_adaptive_bundle",
]
