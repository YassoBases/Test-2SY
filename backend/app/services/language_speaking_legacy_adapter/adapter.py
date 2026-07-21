"""Legacy Speaking adapter (S0) — freeze-wrap boundary for flat legacy services.

RESPONSIBILITY: The ONLY package permitted to import remaining legacy flat modules
(transcription, pronunciation, reply TTS, coach). New speaking packages must route
through this adapter until S7+ migration.

Additional Exercises (conversation / shadowing / scenarios / prompt drills) were
removed from the product surface. Those exclusive flat modules are gone.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Documented mapping — legacy module → canonical target (S7+)
LEGACY_MODULE_MAP: dict[str, str] = {
    "language_transcription_service": "SpeechTranscriptionProvider (legacy impl)",
    "language_pronunciation_service": "pronunciation analysis (legacy Claude+STT)",
    "language_speaking_coach_service": "coach (UNWIRED — replace with language_speaking_coach)",
    "language_reply_tts_service": "SpeakingSpeechOutputProvider (Supertonic legacy wrapper)",
    "speaking_coach_service": "standalone /speaking/coach API (in-memory, separate from main flow)",
    "speaking_coach_prompts": "standalone coach prompt templates",
}

# Known runtime blockers tracked for S0 — fix in hotfix PR, not S0 implementation.
KNOWN_RUNTIME_BLOCKERS: tuple[dict[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class LegacyTurnPayload:
    """Opaque legacy turn result — adapter normalizes to canonical types in S7+."""

    source_module: str
    raw: dict[str, Any]
    adapter_version: str = "0.1.0"


class SpeakingLegacyAdapter:
    """S0 interface — documents boundary; passthrough implementations in S7+."""

    adapter_version: str = "0.1.0"

    @staticmethod
    def legacy_modules() -> dict[str, str]:
        return dict(LEGACY_MODULE_MAP)

    @staticmethod
    def known_blockers() -> tuple[dict[str, str], ...]:
        return KNOWN_RUNTIME_BLOCKERS

    async def adapt_conversation_turn(self, *, raw_result: dict[str, object]) -> LegacyTurnPayload:
        """Retired Additional Exercises path — kept for S0 contract shape only."""
        return LegacyTurnPayload(source_module="retired_additional_exercises", raw=dict(raw_result))

    async def adapt_prompt_submit(self, *, raw_result: dict[str, object]) -> LegacyTurnPayload:
        """Retired Additional Exercises prompt path — kept for S0 contract shape only."""
        return LegacyTurnPayload(source_module="retired_additional_exercises", raw=dict(raw_result))
