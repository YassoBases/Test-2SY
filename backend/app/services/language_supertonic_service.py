"""Supertonic TTS adapter for the language-learning module."""

from __future__ import annotations

import asyncio
import logging
import time
from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings
from app.services.tts_service import prepare_synthesis_text

logger = logging.getLogger(__name__)
settings = get_settings()

SUPERTONIC_MODEL_REPO = "Supertone/supertonic-3"

_CUDA_PROVIDER = "CUDAExecutionProvider"
_CPU_PROVIDER = "CPUExecutionProvider"

_engine_init_count = 0
_prewarm_seconds: float | None = None
_active_onnx_provider: str | None = None
_nvidia_dll_dirs_registered = False


def _register_nvidia_cuda_dll_directories() -> None:
    """Register pip-installed NVIDIA CUDA/cuDNN DLL dirs on Windows (no-op if absent)."""
    global _nvidia_dll_dirs_registered
    if _nvidia_dll_dirs_registered:
        return
    _nvidia_dll_dirs_registered = True

    import os
    import sys

    if sys.platform != "win32":
        return

    try:
        import site
        from pathlib import Path

        bin_dirs: list[str] = []
        for site_dir in site.getsitepackages():
            nvidia_root = Path(site_dir) / "nvidia"
            if not nvidia_root.is_dir():
                continue
            for bin_dir in sorted(nvidia_root.glob("*/bin")):
                if bin_dir.is_dir():
                    path_str = str(bin_dir)
                    bin_dirs.append(path_str)
                    os.add_dll_directory(path_str)

        if bin_dirs:
            # ONNX Runtime CUDA provider resolves dependent DLLs via PATH on Windows.
            os.environ["PATH"] = os.pathsep.join(bin_dirs) + os.pathsep + os.environ.get("PATH", "")
    except Exception as exc:
        logger.debug("NVIDIA DLL path registration skipped: %s", exc)


def resolve_supertonic_onnx_providers() -> list[str]:
    """Return ONNX execution providers for Supertonic (CUDA first when available)."""
    _register_nvidia_cuda_dll_directories()
    try:
        import onnxruntime as ort

        available = frozenset(ort.get_available_providers())
    except Exception as exc:
        logger.debug("ONNX Runtime unavailable for provider detection: %s", exc)
        return [_CPU_PROVIDER]

    if _CUDA_PROVIDER in available:
        return [_CUDA_PROVIDER, _CPU_PROVIDER]
    return [_CPU_PROVIDER]


def primary_supertonic_onnx_provider() -> str:
    """Primary ONNX provider Supertonic will use (for startup logging)."""
    return resolve_supertonic_onnx_providers()[0]


def active_supertonic_onnx_provider() -> str | None:
    """Provider used by the initialized engine, or None before first init."""
    return _active_onnx_provider


def _apply_supertonic_provider_config() -> str:
    """Patch supertonic DEFAULT_ONNX_PROVIDERS before TTS() construction."""
    global _active_onnx_provider
    _register_nvidia_cuda_dll_directories()
    providers = resolve_supertonic_onnx_providers()
    try:
        import supertonic.config as supertonic_config
        import supertonic.loader as supertonic_loader

        supertonic_config.DEFAULT_ONNX_PROVIDERS = providers
        # Importing supertonic.config runs supertonic.__init__, which may bind CPU
        # defaults into loader before this patch — update loader too.
        supertonic_loader.DEFAULT_ONNX_PROVIDERS = providers
    except Exception as exc:
        logger.warning("Could not configure Supertonic ONNX providers: %s", exc)
        _active_onnx_provider = _CPU_PROVIDER
        return _CPU_PROVIDER

    _active_onnx_provider = providers[0]
    return providers[0]


def language_tts_audio_extension() -> str:
    return ".wav"


def language_tts_audio_mime_type() -> str:
    return "audio/wav"


def language_tts_enabled() -> bool:
    return bool(settings.ENABLE_TTS and (settings.LANGUAGE_TTS_PROVIDER or "").strip().lower() == "supertonic")


def engine_init_count() -> int:
    """How many times TTS() was constructed (expect 1 after startup prewarm)."""
    return _engine_init_count


def prewarm_elapsed_seconds() -> float | None:
    """Seconds spent in startup prewarm, or None if skipped/disabled."""
    return _prewarm_seconds


@lru_cache(maxsize=1)
def _tts_engine():
    global _engine_init_count
    provider = _apply_supertonic_provider_config()
    logger.info("Supertonic ONNX Provider: %s", provider)
    from supertonic import TTS

    started = time.perf_counter()
    engine = TTS(auto_download=bool(settings.LANGUAGE_SUPERTONIC_AUTO_DOWNLOAD))
    _engine_init_count += 1
    logger.info(
        "Supertonic TTS engine initialized model=%s voice_default=%s init_count=%s elapsed_s=%.2f",
        SUPERTONIC_MODEL_REPO,
        settings.LANGUAGE_SUPERTONIC_VOICE or "M1",
        _engine_init_count,
        time.perf_counter() - started,
    )
    return engine


@lru_cache(maxsize=16)
def _voice_style(voice_name: str):
    return _tts_engine().get_voice_style(voice_name)


def prewarm_supertonic_engine() -> float:
    """Load Supertone/supertonic-3 and the default voice style once at startup."""
    global _prewarm_seconds
    if not language_tts_enabled():
        logger.info("Supertonic prewarm skipped (ENABLE_TTS or LANGUAGE_TTS_PROVIDER not supertonic)")
        _prewarm_seconds = 0.0
        return 0.0

    voice = (settings.LANGUAGE_SUPERTONIC_VOICE or "M1").strip() or "M1"
    started = time.perf_counter()
    _tts_engine()
    _voice_style(voice)
    elapsed = time.perf_counter() - started
    _prewarm_seconds = elapsed
    logger.info(
        "Supertonic prewarm complete model=%s voice=%s startup_s=%.2f init_count=%s",
        SUPERTONIC_MODEL_REPO,
        voice,
        elapsed,
        _engine_init_count,
    )
    return elapsed


def _synthesize_sync(text: str, *, language: str, output_path: Path, voice_name: str) -> bool:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    engine = _tts_engine()
    style = _voice_style(voice_name)
    started = time.perf_counter()
    wav, _duration = engine.synthesize(text, voice_style=style, lang=language)
    engine.save_audio(wav, str(output_path))
    ok = output_path.exists() and output_path.stat().st_size > 0
    logger.info(
        "Supertonic synthesis model=%s voice=%s chars=%s elapsed_s=%.2f bytes=%s init_count=%s",
        SUPERTONIC_MODEL_REPO,
        voice_name,
        len(text),
        time.perf_counter() - started,
        output_path.stat().st_size if ok else 0,
        _engine_init_count,
    )
    return ok


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


async def synthesize_language_speech_segments(
    segments: list[tuple[str, str]],
    *,
    language: str = "en",
    output_path: Path,
    pause_ms: int = 350,
) -> bool:
    """Synthesize ordered text segments with per-segment voices into one WAV file."""
    if not segments or not language_tts_enabled():
        return False

    lang = (language or "en").strip().lower()
    try:
        return await asyncio.to_thread(
            _synthesize_segments_sync,
            segments,
            language=lang,
            output_path=output_path,
            pause_ms=pause_ms,
        )
    except Exception as exc:
        logger.warning("Supertonic multi-segment synthesis failed: %s", exc)
        return False


def _synthesize_segments_sync(
    segments: list[tuple[str, str]],
    *,
    language: str,
    output_path: Path,
    pause_ms: int,
) -> bool:
    import numpy as np

    output_path.parent.mkdir(parents=True, exist_ok=True)
    engine = _tts_engine()
    wav_parts: list[np.ndarray] = []
    sample_rate: int | None = None

    for text, voice_name in segments:
        cleaned = prepare_synthesis_text(text)
        if not cleaned:
            continue
        voice = (voice_name or settings.LANGUAGE_SUPERTONIC_VOICE or "M1").strip() or "M1"
        style = _voice_style(voice)
        wav, _duration = engine.synthesize(cleaned, voice_style=style, lang=language)
        arr = np.asarray(wav)
        if arr.ndim > 1:
            arr = arr.squeeze()
        if sample_rate is None:
            sample_rate = getattr(engine, "sample_rate", None) or 24000
        wav_parts.append(arr.astype(np.float32))
        if len(segments) > 1 and pause_ms > 0:
            pause_samples = int(sample_rate * pause_ms / 1000)
            wav_parts.append(np.zeros(pause_samples, dtype=np.float32))

    if not wav_parts:
        return False

    if len(wav_parts) > 1 and pause_ms > 0:
        wav_parts = wav_parts[:-1]

    combined = np.concatenate(wav_parts)
    engine.save_audio(combined, str(output_path))
    ok = output_path.exists() and output_path.stat().st_size > 0
    logger.info(
        "Supertonic multi-segment synthesis voices=%s segments=%s bytes=%s",
        sorted({v for _, v in segments}),
        len(segments),
        output_path.stat().st_size if ok else 0,
    )
    return ok
