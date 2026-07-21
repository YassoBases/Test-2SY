from __future__ import annotations

from types import SimpleNamespace

from app.services import language_tts_service as tts


class _FakeScalars:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class _FakeResult:
    def __init__(self, rows=None, scalar=None):
        self._rows = rows or []
        self._scalar = scalar

    def scalars(self):
        return _FakeScalars(self._rows)

    def scalar_one_or_none(self):
        return self._scalar


class _FakeDB:
    def __init__(self, item=None, cache_rows=None):
        self.item = item
        self.cache_rows = cache_rows or []
        self.added = []

    async def get(self, _model, _content_item_id):
        return self.item

    async def execute(self, _query):
        return _FakeResult(rows=self.cache_rows)

    def add(self, row):
        self.added.append(row)

    async def flush(self):
        return None


def _settings(tmp_path, *, provider="supertonic", openai_key="sk-test"):
    return SimpleNamespace(
        ENABLE_TTS=True,
        LANGUAGE_TTS_PROVIDER=provider,
        OPENAI_API_KEY=openai_key,
        UPLOAD_DIR=str(tmp_path),
        SPEAKING_TTS_MODEL="gpt-4o-mini-tts",
        SPEAKING_TTS_VOICE="verse",
        SPEAKING_TTS_TIMEOUT_SECONDS=30,
    )


async def test_lesson_audio_falls_back_to_openai_when_supertonic_is_unavailable(monkeypatch, tmp_path):
    item = SimpleNamespace(
        id=123,
        body_json={"audio_transcript": "I am listening to a short lesson."},
        title="Listening lesson",
    )
    db = _FakeDB(item=item)
    monkeypatch.setattr(tts, "settings", _settings(tmp_path))

    async def fake_supertonic(*_args, **_kwargs):
        return None

    async def fake_openai_write(text, dest):
        assert text == "I am listening to a short lesson."
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"mp3-audio")
        return True

    monkeypatch.setattr(tts, "_synthesize_supertonic", fake_supertonic)
    monkeypatch.setattr(tts, "_write_openai_speech", fake_openai_write)

    result = await tts.get_lesson_audio(db, content_item_id=123)

    assert result == {
        "public_url": "/uploads/language_audio/123/openai.mp3",
        "duration_seconds": None,
        "voice_source": "openai",
    }
    assert db.added[0].voice_source == "openai"
    assert (tmp_path / "language_audio" / "123" / "openai.mp3").read_bytes() == b"mp3-audio"


async def test_lesson_audio_reuses_openai_cache_when_file_exists(monkeypatch, tmp_path):
    storage_key = "language_audio/456/openai.mp3"
    disk_path = tmp_path / storage_key
    disk_path.parent.mkdir(parents=True, exist_ok=True)
    disk_path.write_bytes(b"cached-mp3")
    cached = SimpleNamespace(
        public_url="/uploads/language_audio/456/openai.mp3",
        duration_seconds=None,
        voice_source="openai",
        audio_storage_key=storage_key,
    )
    db = _FakeDB(cache_rows=[cached])
    monkeypatch.setattr(tts, "settings", _settings(tmp_path))

    result = await tts.get_lesson_audio(db, content_item_id=456)

    assert result == {
        "public_url": "/uploads/language_audio/456/openai.mp3",
        "duration_seconds": None,
        "voice_source": "openai",
    }
    assert db.added == []


async def test_lesson_audio_does_not_use_openai_when_language_tts_is_disabled(monkeypatch, tmp_path):
    item = SimpleNamespace(
        id=789,
        body_json={"audio_transcript": "This should not be synthesized."},
        title="Listening lesson",
    )
    db = _FakeDB(item=item)
    calls = []
    monkeypatch.setattr(tts, "settings", _settings(tmp_path, provider="disabled"))

    async def fake_supertonic(*_args, **_kwargs):
        return None

    async def fake_openai_write(*_args, **_kwargs):
        calls.append("openai")
        return True

    monkeypatch.setattr(tts, "_synthesize_supertonic", fake_supertonic)
    monkeypatch.setattr(tts, "_write_openai_speech", fake_openai_write)

    result = await tts.generate_lesson_audio(db, content_item_id=789)

    assert result is None
    assert calls == []
