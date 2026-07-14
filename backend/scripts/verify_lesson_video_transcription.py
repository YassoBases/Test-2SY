"""Verify faster-whisper lesson video transcription (Phase 6.2).

Usage (from backend/):
    python scripts/verify_lesson_video_transcription.py
    python scripts/verify_lesson_video_transcription.py --benchmark path/to/video.mp4
"""

from __future__ import annotations

import argparse
import asyncio
import inspect
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _static_checks() -> dict[str, bool]:
    from app.core.config import get_settings
    from app.services import voice_service

    settings = get_settings()
    vs = inspect.getsource(voice_service)
    lp_path = Path(__file__).resolve().parents[1] / "app" / "services" / "lesson_processor.py"
    lp = lp_path.read_text(encoding="utf-8")
    tasks_path = Path(__file__).resolve().parents[1] / "app" / "services" / "lesson_processing_tasks.py"
    tasks_src = tasks_path.read_text(encoding="utf-8")

    faster_fn = inspect.getsource(voice_service._transcribe_wav_faster_whisper)
    audio_fn = inspect.getsource(voice_service._transcribe_with_whisper_sync)
    gemini_fn = inspect.getsource(voice_service._transcribe_video_with_gemini)
    lesson_video_fn = inspect.getsource(voice_service.transcribe_lesson_video)

    return {
        "lesson_processor_uses_transcribe_lesson_video": "transcribe_lesson_video" in lp
        and "transcribe_audio(video_path" not in lp,
        "transcribe_lesson_video_exists": hasattr(voice_service, "transcribe_lesson_video"),
        "ffmpeg_extract_present": "_extract_video_to_wav" in vs,
        "structured_logging_present": "_log_video_transcription" in vs
        and "VideoTranscriptionResult" in vs,
        "faster_whisper_uses_arabic": 'language="ar"' in faster_fn
        or "language=language" in faster_fn,
        "no_small_en_in_lesson_video": "small.en" not in vs.split("async def transcribe_audio")[0],
        "no_language_en_in_lesson_video": 'language="en"' not in vs.split("async def transcribe_audio")[0],
        "transcribe_audio_unchanged_arabic": 'language="ar"' in audio_fn,
        "gemini_active_wait": "ACTIVE" in gemini_fn and "get_file" in gemini_fn,
        "gemini_600s_timeout": str(settings.LESSON_VIDEO_GEMINI_TIMEOUT_SECONDS) == "600"
        and "timeout_s" in lesson_video_fn,
        "arabic_gemini_video_prompt": "بالعربية" in voice_service.GEMINI_TRANSCRIBE_VIDEO_PROMPT,
        "stale_job_recovery_present": "_recover_stale_lesson_job" in tasks_src
        and "STALE_JOB_SECONDS" in tasks_src,
        "whisper_language_config_ar": settings.LESSON_VIDEO_WHISPER_LANGUAGE == "ar",
        "turbo_maps_to_large_v3_turbo": voice_service._FASTER_WHISPER_MODEL_ALIASES.get("turbo")
        == "large-v3-turbo",
    }


async def _flow_mock_checks() -> dict[str, bool]:
    import os

    from app.services import voice_service

    fd, video_name = tempfile.mkstemp(suffix=".mp4")
    os.close(fd)
    video_path = Path(video_name)
    try:
        video_path.write_bytes(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00")

        whisper_result = voice_service.VideoTranscriptionResult(
            text="مرحبا بالطلاب",
            engine="faster-whisper",
            model="large-v3-turbo",
            duration_s=1.2,
        )

        with (
            patch.object(
                voice_service,
                "_transcribe_lesson_video_whisper_sync",
                return_value=whisper_result,
            ) as whisper_mock,
            patch.object(
                voice_service,
                "_transcribe_video_with_gemini",
                new_callable=AsyncMock,
            ) as gemini_mock,
        ):
            text = await voice_service.transcribe_lesson_video(video_path)
            whisper_called = whisper_mock.called
            gemini_not_called = not gemini_mock.called
            whisper_text = text == "مرحبا بالطلاب"

        empty_result = voice_service.VideoTranscriptionResult(
            text="",
            engine="none",
            model="",
            duration_s=0.5,
            fallback_reason="faster_whisper_empty",
        )
        gemini_mock.reset_mock()
        with (
            patch.object(
                voice_service,
                "_transcribe_lesson_video_whisper_sync",
                return_value=empty_result,
            ),
            patch.object(
                voice_service,
                "_transcribe_video_with_gemini",
                new_callable=AsyncMock,
                return_value="نص من جيميني",
            ) as gemini_mock,
            patch.object(voice_service.settings, "GEMINI_API_KEY", "test-key"),
        ):
            text = await voice_service.transcribe_lesson_video(video_path)
            gemini_fallback = gemini_mock.called and text == "نص من جيميني"
            gemini_timeout = gemini_mock.call_args.kwargs.get("timeout_s") == 600

        return {
            "whisper_success_skips_gemini": whisper_called and gemini_not_called and whisper_text,
            "empty_whisper_triggers_gemini": gemini_fallback and gemini_timeout,
        }
    finally:
        video_path.unlink(missing_ok=True)


def _make_silent_wav(path: Path, *, seconds: float = 1.0, sample_rate: int = 16000) -> None:
    n_frames = int(sample_rate * seconds)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * n_frames)


async def _benchmark(video_path: Path | None) -> dict:
    import os

    from app.services import voice_service

    if video_path and video_path.exists():
        started = time.perf_counter()
        text = await voice_service.transcribe_lesson_video(video_path)
        elapsed = time.perf_counter() - started
        return {
            "mode": "video_file",
            "path": str(video_path),
            "duration_s": round(elapsed, 2),
            "chars": len(text),
            "preview": text[:120],
        }

    wav_fd, wav_name = tempfile.mkstemp(suffix=".wav")
    os.close(wav_fd)
    wav_path = Path(wav_name)
    try:
        _make_silent_wav(wav_path, seconds=2.0)
        started = time.perf_counter()
        result = await asyncio.to_thread(voice_service._transcribe_lesson_video_whisper_sync, wav_path)
        elapsed = time.perf_counter() - started
        return {
            "mode": "silent_wav_whisper_path",
            "path": str(wav_path),
            "duration_s": round(elapsed, 2),
            "engine": result.engine if result else "none",
            "fallback_reason": result.fallback_reason if result else None,
            "note": "Silent audio — empty transcript expected; measures ffmpeg-less whisper pipeline timing",
        }
    finally:
        wav_path.unlink(missing_ok=True)


def _print_results(title: str, results: dict[str, bool | str | float | int | None]) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    for key, value in results.items():
        mark = "PASS" if value is True else ("FAIL" if value is False else "INFO")
        print(f"  [{mark}] {key}: {value}")


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, default=None, help="Optional lesson video for timing")
    args = parser.parse_args()

    print("Phase 6.2 — verify_lesson_video_transcription")

    static = _static_checks()
    _print_results("Static checks", static)

    flow = await _flow_mock_checks()
    _print_results("Flow checks (mocked)", flow)

    benchmark = (
        await _benchmark(args.benchmark)
        if args.benchmark
        else {"mode": "skipped", "note": "Pass --benchmark path/to/video.mp4 to load and time the model."}
    )
    _print_results("Benchmark", benchmark)

    all_bool = {**static, **flow}
    failed = [k for k, v in all_bool.items() if v is False]
    if failed:
        print(f"\nFAILED ({len(failed)}): {', '.join(failed)}")
        return 1

    print(f"\nAll {len(all_bool)} checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
