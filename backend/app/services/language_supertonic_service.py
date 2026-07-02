"""Supertonic TTS adapter for the language-learning module."""

from __future__ import annotations

import asyncio
import logging
from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings
from app.services.tts_service import prepare_synthesis_text

logger = logging.getLogger(__name__)
settings = get_settings()


def language_tts_audio_extension() -> str:
    return ".wav"


def language_tts_audio_mime_type() -> str:
    return "audio/wav"


def language_tts_enabled() -> bool:
    return bool(settings.ENABLE_TTS and (settings.LANGUAGE_TTS_PROVIDER or "").strip().lower() == "supertonic")


@lru_cache(maxsize=1)
def _tts_engine():
    from supertonic import TTS

    return TTS(auto_download=bool(settings.LANGUAGE_SUPERTONIC_AUTO_DOWNLOAD))


@lru_cache(maxsize=16)
def _voice_style(voice_name: str):
    return _tts_engine().get_voice_style(voice_name)


def _synthesize_sync(text: str, *, language: str, output_path: Path, voice_name: str) -> bool:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    engine = _tts_engine()
    style = _voice_style(voice_name)
    wav, _duration = engine.synthesize(text, voice_style=style, lang=language)
    engine.save_audio(wav, str(output_path))
    return output_path.exists() and output_path.stat().st_size > 0


async def synthesize_language_speech(
    text: str,
    *,
    language: str = "en",
    output_path: Path,
    voice_name: str | None = None,
) -> bool:
    """Generate speech with Supertone/supertonic-3."""

    cleaned = prepare_synthesis_text(text)
    if not cleaned or not language_tts_enabled():
        return False

    voice = (voice_name or settings.LANGUAGE_SUPERTONIC_VOICE or "M1").strip() or "M1"
    lang = (language or "en").strip().lower()
    try:
        return await asyncio.to_thread(
            _synthesize_sync,
            cleaned,
            language=lang,
            output_path=output_path,
            voice_name=voice,
        )
    except Exception as exc:
        logger.warning("Supertonic synthesis failed: %s", exc)
        return False
