"""Listening lesson audio renderer — gender-aware Supertonic synthesis."""

from __future__ import annotations

import logging
from pathlib import Path

from app.services.language_listening_tts.speakers import build_synthesis_segments
from app.services.language_supertonic_service import (
    language_tts_audio_extension,
    synthesize_language_speech_segments,
)

logger = logging.getLogger(__name__)


def listening_cache_filename(segments: list[tuple[str, str]]) -> str:
    voices = {voice for _, voice in segments}
    if len(segments) <= 1 and len(voices) <= 1:
        return f"supertonic{language_tts_audio_extension()}"
    return f"supertonic_multivoice{language_tts_audio_extension()}"


async def synthesize_listening_lesson_audio(
    body: dict | None,
    *,
    output_path: Path,
    language: str = "en",
) -> bool:
    segments = build_synthesis_segments(body)
    if not segments:
        return False
    ok = await synthesize_language_speech_segments(
        segments,
        language=language,
        output_path=output_path,
    )
    if ok:
        logger.info(
            "Listening multivoice synthesis segments=%s voices=%s",
            len(segments),
            sorted({v for _, v in segments}),
        )
    return ok
