"""English speech-to-text for the Language module — OpenAI GPT-4o Transcribe with Whisper fallback."""

from __future__ import annotations

import asyncio
import logging
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

import httpx

from app.core.config import get_settings
from app.services.model_cache import configure_model_cache

logger = logging.getLogger(__name__)
settings = get_settings()

_conversation_whisper_model = None
_OPENAI_TRANSCRIPTIONS_URL = "https://api.openai.com/v1/audio/transcriptions"

DEFAULT_INITIAL_PROMPT = (
    "English speaking practice. The student introduces themselves. "
    "My name is Hamza. My name are Hamza Al-Kuzbari."
)


@dataclass
class ConversationTranscription:
    text: str
    engine: str
    model: str
    duration_s: float = 0.0
    avg_logprob: float | None = None
    no_speech_prob: float | None = None
    language_probability: float | None = None
    low_confidence: bool = False
    raw_text: str = ""
    meta: dict = field(default_factory=dict)


def _language_stt_provider() -> str:
    return (settings.LANGUAGE_STT_PROVIDER or "openai").strip().lower()


def _openai_api_key() -> str:
    return (settings.OPENAI_API_KEY or "").strip()


def _language_stt_model() -> str:
    return (settings.LANGUAGE_STT_MODEL or "gpt-4o-transcribe").strip()


def _should_use_openai_stt() -> bool:
    return _language_stt_provider() == "openai" and bool(_openai_api_key())


def _allow_whisper_fallback() -> bool:
    return bool(settings.LANGUAGE_STT_ALLOW_WHISPER_FALLBACK)


def _resolve_ffmpeg() -> str | None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def _normalize_to_wav_16k(source: Path) -> Path:
    """Decode browser webm/opus to mono 16 kHz wav — required for reliable Whisper accuracy."""
    ffmpeg = _resolve_ffmpeg()
    if not ffmpeg:
        raise RuntimeError("ffmpeg not available for audio normalization")

    out = Path(tempfile.mkstemp(suffix=".wav")[1])
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(source),
        "-ar",
        "16000",
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        str(out),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not out.exists() or out.stat().st_size == 0:
        out.unlink(missing_ok=True)
        raise RuntimeError(f"ffmpeg normalize failed: {(result.stderr or result.stdout)[-500:]}")
    return out


def _get_conversation_whisper_model():
    global _conversation_whisper_model
    if _conversation_whisper_model is not None:
        return _conversation_whisper_model

    configure_model_cache()

    from faster_whisper import WhisperModel

    model_id = (settings.LANGUAGE_CONVERSATION_WHISPER_MODEL or "small.en").strip()
    compute = (settings.LANGUAGE_CONVERSATION_WHISPER_COMPUTE_TYPE or "float32").strip()
    logger.info(
        "Loading conversation faster-whisper model=%s compute_type=%s device=cpu",
        model_id,
        compute,
    )
    _conversation_whisper_model = WhisperModel(model_id, device="cpu", compute_type=compute)
    return _conversation_whisper_model


def _initial_prompt() -> str:
    raw = (settings.LANGUAGE_CONVERSATION_WHISPER_INITIAL_PROMPT or "").strip()
    return raw or DEFAULT_INITIAL_PROMPT


def _segment_confidence(segments: list) -> tuple[float | None, float | None]:
    if not segments:
        return None, None
    logprobs = [s.avg_logprob for s in segments if getattr(s, "avg_logprob", None) is not None]
    no_speech = [s.no_speech_prob for s in segments if getattr(s, "no_speech_prob", None) is not None]
    avg_logprob = sum(logprobs) / len(logprobs) if logprobs else None
    max_no_speech = max(no_speech) if no_speech else None
    return avg_logprob, max_no_speech


def _is_low_confidence(avg_logprob: float | None, no_speech_prob: float | None) -> bool:
    if no_speech_prob is not None and no_speech_prob >= 0.55:
        return True
    if avg_logprob is not None and avg_logprob <= -0.85:
        return True
    return False


def _transcribe_faster_whisper(wav_path: Path) -> ConversationTranscription:
    model = _get_conversation_whisper_model()
    model_id = (settings.LANGUAGE_CONVERSATION_WHISPER_MODEL or "small.en").strip()
    beam = max(1, int(settings.LANGUAGE_CONVERSATION_WHISPER_BEAM_SIZE or 5))
    vad = bool(settings.LANGUAGE_CONVERSATION_WHISPER_VAD)

    segments, info = model.transcribe(
        str(wav_path),
        language="en",
        beam_size=beam,
        best_of=beam,
        vad_filter=vad,
        initial_prompt=_initial_prompt(),
        condition_on_previous_text=False,
    )
    seg_list = list(segments)
    text = "".join(s.text for s in seg_list).strip()
    avg_logprob, no_speech_prob = _segment_confidence(seg_list)

    return ConversationTranscription(
        text=text,
        raw_text=text,
        engine="faster-whisper",
        model=model_id,
        duration_s=float(info.duration or 0.0),
        avg_logprob=avg_logprob,
        no_speech_prob=no_speech_prob,
        language_probability=float(info.language_probability or 0.0),
        low_confidence=_is_low_confidence(avg_logprob, no_speech_prob),
        meta={
            "beam_size": beam,
            "vad_filter": vad,
            "compute_type": settings.LANGUAGE_CONVERSATION_WHISPER_COMPUTE_TYPE,
            "segment_count": len(seg_list),
            "fallback": True,
        },
    )


def _transcribe_openai(source_path: Path) -> ConversationTranscription:
    """Transcribe with OpenAI Audio API (gpt-4o-transcribe)."""
    api_key = _openai_api_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    model = _language_stt_model()
    prompt = _initial_prompt()

    with source_path.open("rb") as audio_file:
        response = httpx.post(
            _OPENAI_TRANSCRIPTIONS_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            files={"file": (source_path.name, audio_file, "application/octet-stream")},
            data={
                "model": model,
                "language": "en",
                "response_format": "json",
                "prompt": prompt,
            },
            timeout=httpx.Timeout(120.0),
        )

    if response.status_code >= 400:
        raise RuntimeError(
            f"OpenAI transcription failed: status={response.status_code} detail={response.text[:500]}"
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError("OpenAI transcription returned invalid JSON") from exc

    text = str(payload.get("text") or "").strip()
    return ConversationTranscription(
        text=text,
        raw_text=text,
        engine="openai",
        model=model,
        low_confidence=not text,
        meta={"provider": "openai", "fallback": False},
    )


def _transcribe_whisper_sync(source_path: Path) -> ConversationTranscription:
    wav_path: Path | None = None
    try:
        wav_path = _normalize_to_wav_16k(source_path)
        result = _transcribe_faster_whisper(wav_path)
        result.meta["normalized_wav"] = True
        return result
    finally:
        if wav_path and wav_path.exists():
            try:
                wav_path.unlink()
            except OSError:
                pass


def _transcribe_sync(source_path: Path) -> tuple[ConversationTranscription, float]:
    started = time.perf_counter()

    if _should_use_openai_stt():
        try:
            result = _transcribe_openai(source_path)
            elapsed = time.perf_counter() - started
            return result, elapsed
        except Exception as exc:
            if not _allow_whisper_fallback():
                raise RuntimeError(
                    f"OpenAI language STT failed and Whisper fallback is disabled: {exc}"
                ) from exc
            logger.warning("OpenAI language STT failed, falling back to faster-whisper: %s", exc)

    if not _allow_whisper_fallback():
        raise RuntimeError("Language STT unavailable: OpenAI is not configured and Whisper fallback is disabled")

    if not settings.ENABLE_WHISPER:
        raise RuntimeError("Language STT unavailable: OpenAI failed and Whisper is disabled")

    result = _transcribe_whisper_sync(source_path)
    elapsed = time.perf_counter() - started
    return result, elapsed


async def transcribe_english_audio(data: bytes, *, suffix: str = ".webm") -> ConversationTranscription:
    """Transcribe uploaded audio to English text with confidence metadata."""
    if not data:
        return ConversationTranscription(text="", raw_text="", engine="none", model="")

    if not _should_use_openai_stt() and not settings.ENABLE_WHISPER:
        logger.info("Language STT unavailable — OpenAI not configured and Whisper disabled")
        return ConversationTranscription(text="", raw_text="", engine="disabled", model="")

    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(data)
            tmp_path = Path(tmp.name)
        result, elapsed = await asyncio.to_thread(_transcribe_sync, tmp_path)
        logger.info(
            "Conversation transcription engine=%s model=%s duration_s=%.2f text=%r "
            "avg_logprob=%s no_speech_prob=%s low_confidence=%s",
            result.engine,
            result.model,
            elapsed,
            result.text,
            result.avg_logprob,
            result.no_speech_prob,
            result.low_confidence,
        )
        return result
    except Exception as exc:
        logger.warning("English transcription failed: %s", exc)
        return ConversationTranscription(text="", raw_text="", engine="error", model="", meta={"error": str(exc)})
    finally:
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
