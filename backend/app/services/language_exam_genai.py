"""Audio-native exam engine — Claude structured JSON (transcript via Language STT).

Used by the placement exam's SPEAKING section: audio is transcribed with the existing
Language STT provider (OpenAI GPT-4o Transcribe), then Claude assesses content and
delivery from the transcript using the same rubric prompts.
"""

from __future__ import annotations

import logging

from app.core.config import get_settings
from app.schemas.language_exam import SpeakingTurnAssessment
from app.services.claude_service import generate_claude_json_model, is_claude_configured

logger = logging.getLogger(__name__)
settings = get_settings()

# Accepted spoken-answer container types (browser MediaRecorder + common uploads).
ACCEPTED_AUDIO_MIME: dict[str, str] = {
    "audio/webm": ".webm",
    "audio/ogg": ".ogg",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/wave": ".wav",
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
    "audio/mp4": ".m4a",
    "audio/x-m4a": ".m4a",
    "audio/aac": ".aac",
    "audio/flac": ".flac",
}


class ExamLlmUnavailable(RuntimeError):
    """Raised when the audio exam engine cannot serve a request (no key / model)."""


def _suffix_for(mime: str) -> str:
    return ACCEPTED_AUDIO_MIME.get((mime or "").split(";")[0].strip().lower(), ".webm")


async def assess_speaking_turn(
    *, transcript: str, system: str, prompt: str
) -> SpeakingTurnAssessment:
    """Assess one verified STT transcript and preserve it verbatim in the result."""
    transcript = (transcript or "").strip()
    if not transcript:
        raise ExamLlmUnavailable("Empty speech transcript")
    if not is_claude_configured():
        raise ExamLlmUnavailable("ANTHROPIC_API_KEY is not configured")

    enriched_prompt = (
        f'{prompt}\n\nVerified GPT-4o speech-to-text transcript:\n"""\n{transcript}\n"""\n'
        "Use this exact transcript for the transcription field. Evaluate delivery conservatively "
        "from the wording and visible disfluencies."
    )
    result = await generate_claude_json_model(
        enriched_prompt,
        system=system,
        model_type=SpeakingTurnAssessment,
        temperature=0.3,
        max_output_tokens=2048,
    )
    if result is None:
        raise ExamLlmUnavailable("Claude speaking assessment returned no result")
    return result.model_copy(update={"transcription": transcript})


# Backward-compatible alias for existing imports.
GenAIUnavailable = ExamLlmUnavailable
