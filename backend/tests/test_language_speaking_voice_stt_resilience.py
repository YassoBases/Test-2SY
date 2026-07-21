from __future__ import annotations

import asyncio
from types import SimpleNamespace

from app.services.language_speaking_discussion import voice_io
from app.services.language_speaking_live_bridge import engine as live_bridge_engine


def _stub_normalization(_artifact, _audio_bytes):
    return SimpleNamespace(), b"normalized-wav", ()


def test_discussion_voice_uses_shared_stt_when_dedicated_providers_fail(monkeypatch):
    monkeypatch.setattr(voice_io, "normalize_audio_with_bytes", _stub_normalization)
    monkeypatch.setattr(
        voice_io,
        "build_transcription_provider",
        lambda _name=None: (_ for _ in ()).throw(RuntimeError("provider down")),
    )

    async def fake_shared_stt(audio_bytes, *, suffix=".webm", audio_duration_s=None):
        assert audio_bytes == b"webm-audio"
        assert suffix == ".webm"
        assert audio_duration_s is None
        return SimpleNamespace(text="I am ready.")

    monkeypatch.setattr(voice_io, "transcribe_english_audio", fake_shared_stt)

    transcript, confidence = asyncio.run(
        voice_io.transcribe_discussion_audio(
            b"webm-audio",
            "audio/webm;codecs=opus",
            student_id=1,
            language_id=1,
        )
    )

    assert transcript == "I am ready."
    assert confidence is None


def test_discussion_voice_returns_gentle_retry_when_all_stt_paths_fail(monkeypatch):
    monkeypatch.setattr(voice_io, "normalize_audio_with_bytes", _stub_normalization)
    monkeypatch.setattr(
        voice_io,
        "build_transcription_provider",
        lambda _name=None: (_ for _ in ()).throw(RuntimeError("provider down")),
    )

    async def fake_empty_shared_stt(*_args, **_kwargs):
        return SimpleNamespace(text="", engine="error", meta={"error_code": "stt_unavailable"})

    monkeypatch.setattr(voice_io, "transcribe_english_audio", fake_empty_shared_stt)

    transcript, confidence = asyncio.run(
        voice_io.transcribe_discussion_audio(
            b"webm-audio",
            "audio/webm",
            student_id=1,
            language_id=1,
        )
    )

    assert transcript == ""
    assert confidence is None


def test_scene_practice_voice_uses_shared_stt_when_dedicated_provider_fails(monkeypatch):
    monkeypatch.setattr(live_bridge_engine, "normalize_audio_with_bytes", _stub_normalization)
    monkeypatch.setattr(
        live_bridge_engine,
        "build_transcription_provider",
        lambda: (_ for _ in ()).throw(RuntimeError("provider down")),
    )

    async def fake_shared_stt(audio_bytes, *, suffix=".webm", audio_duration_s=None):
        assert audio_bytes == b"scene-audio"
        assert suffix == ".m4a"
        assert audio_duration_s is None
        return SimpleNamespace(text="I can help you.")

    monkeypatch.setattr(live_bridge_engine, "transcribe_english_audio", fake_shared_stt)

    transcript, confidence = asyncio.run(
        live_bridge_engine._transcribe_student_audio(
            b"scene-audio",
            "audio/mp4",
            student_id=1,
            language_id=1,
        )
    )

    assert transcript == "I can help you."
    assert confidence is None


def test_scene_practice_voice_returns_empty_transcript_when_all_stt_paths_fail(monkeypatch):
    monkeypatch.setattr(live_bridge_engine, "normalize_audio_with_bytes", _stub_normalization)
    monkeypatch.setattr(
        live_bridge_engine,
        "build_transcription_provider",
        lambda: (_ for _ in ()).throw(RuntimeError("provider down")),
    )

    async def fake_empty_shared_stt(*_args, **_kwargs):
        return SimpleNamespace(text="", engine="error", meta={"error_code": "stt_unavailable"})

    monkeypatch.setattr(live_bridge_engine, "transcribe_english_audio", fake_empty_shared_stt)

    transcript, confidence = asyncio.run(
        live_bridge_engine._transcribe_student_audio(
            b"scene-audio",
            "audio/webm",
            student_id=1,
            language_id=1,
        )
    )

    assert transcript == ""
    assert confidence is None
