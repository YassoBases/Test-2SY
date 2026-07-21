"""Lesson audio synthesis for language learning."""

from __future__ import annotations

import asyncio
import logging
import uuid
from pathlib import Path

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.language.content import LanguageContentItem
from app.models.language.tts_cache import LanguageLessonAudioCache
from app.services.language_supertonic_service import language_tts_audio_extension, synthesize_language_speech

logger = logging.getLogger(__name__)
settings = get_settings()

_OPENAI_SPEECH_URL = "https://api.openai.com/v1/audio/speech"
_OPENAI_AUDIO_FORMAT = "mp3"
_OPENAI_AUDIO_MIME = "audio/mpeg"
_SUPERTONIC_SOURCE = "supertonic"
_OPENAI_SOURCE = "openai"


def _lesson_text(item: LanguageContentItem) -> str:
    body = item.body_json or {}
    text = (
        body.get("audio_transcript")
        or body.get("prompt")
        or body.get("text")
        or body.get("passage")  # reading passages — enables read-along narration
        or item.title
        or ""
    )
    return str(text).strip()


def _audio_dir(content_item_id: int) -> Path:
    d = Path(settings.UPLOAD_DIR) / "language_audio" / str(content_item_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _storage_key(dest: Path) -> str:
    rel = dest.resolve().relative_to(Path(settings.UPLOAD_DIR).resolve())
    return "/".join(rel.parts)


async def synthesize_exam_audio(text: str, *, voice: str = "en-US-AriaNeural") -> str | None:
    """Generate public audio for AI exam listening prompts.

    Uses Supertonic only.
    The voice argument is accepted for compatibility with the Fayz exam service.
    """

    cleaned = str(text or "").strip()
    if not cleaned:
        return None

    out_dir = Path(settings.UPLOAD_DIR) / "language_exam_audio"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not settings.ENABLE_TTS:
        return None

    dest = out_dir / f"exam_{uuid.uuid4().hex}{language_tts_audio_extension()}"
    ok = await synthesize_language_speech(
        cleaned,
        language="en",
        output_path=dest,
    )
    if ok:
        return "/uploads/" + _storage_key(dest)
    return None


async def _cache_lookup(
    db: AsyncSession, *, content_item_id: int, teacher_id: int | None
) -> LanguageLessonAudioCache | None:
    voice_sources = (_SUPERTONIC_SOURCE, _OPENAI_SOURCE)
    query = select(LanguageLessonAudioCache).where(
        LanguageLessonAudioCache.content_item_id == content_item_id,
        LanguageLessonAudioCache.voice_source.in_(voice_sources),
    )
    if teacher_id is not None:
        query = query.where(
            (LanguageLessonAudioCache.teacher_id == teacher_id)
            | (LanguageLessonAudioCache.teacher_id.is_(None))
        )
    result = await db.execute(query)
    rows = list(result.scalars().all())
    if not rows:
        return None
    rows.sort(key=lambda r: voice_sources.index(r.voice_source) if r.voice_source in voice_sources else 99)
    return rows[0]


def _out(row: LanguageLessonAudioCache) -> dict:
    return {
        "public_url": row.public_url,
        "duration_seconds": row.duration_seconds,
        "voice_source": row.voice_source,
    }


async def _upsert_cache(
    db: AsyncSession,
    *,
    content_item_id: int,
    voice_source: str,
    teacher_id: int | None,
    storage_key: str,
    public_url: str,
) -> LanguageLessonAudioCache:
    existing = await db.execute(
        select(LanguageLessonAudioCache).where(
            LanguageLessonAudioCache.content_item_id == content_item_id,
            LanguageLessonAudioCache.voice_source == voice_source,
            LanguageLessonAudioCache.teacher_id.is_(None)
            if teacher_id is None
            else LanguageLessonAudioCache.teacher_id == teacher_id,
        )
    )
    row = existing.scalar_one_or_none()
    if row is None:
        row = LanguageLessonAudioCache(
            content_item_id=content_item_id,
            voice_source=voice_source,
            teacher_id=teacher_id,
        )
        db.add(row)
    row.audio_storage_key = storage_key
    row.public_url = public_url
    row.duration_seconds = None
    await db.flush()
    return row


async def _synthesize_supertonic(
    db: AsyncSession,
    *,
    item: LanguageContentItem,
    text: str,
) -> dict | None:
    if not settings.ENABLE_TTS:
        return None

    voice_source = _SUPERTONIC_SOURCE
    cache_teacher_id: int | None = None
    fname = f"{voice_source}{language_tts_audio_extension()}"
    dest = _audio_dir(item.id) / fname

    ok = await synthesize_language_speech(
        text,
        language="en",
        output_path=dest,
    )
    if not ok:
        return None

    storage_key = _storage_key(dest)
    public_url = "/uploads/" + storage_key
    row = await _upsert_cache(
        db,
        content_item_id=item.id,
        voice_source=voice_source,
        teacher_id=cache_teacher_id,
        storage_key=storage_key,
        public_url=public_url,
    )
    return _out(row)


def _openai_tts_enabled() -> bool:
    provider = (getattr(settings, "LANGUAGE_TTS_PROVIDER", "supertonic") or "supertonic").strip().lower()
    api_key = (getattr(settings, "OPENAI_API_KEY", None) or "").strip()
    return bool(settings.ENABLE_TTS and provider != "disabled" and api_key)


def _openai_tts_model() -> str:
    return (
        getattr(settings, "LANGUAGE_OPENAI_TTS_MODEL", None)
        or getattr(settings, "SPEAKING_TTS_MODEL", None)
        or "gpt-4o-mini-tts"
    ).strip()


def _openai_tts_voice() -> str:
    return (
        getattr(settings, "LANGUAGE_OPENAI_TTS_VOICE", None)
        or getattr(settings, "SPEAKING_TTS_VOICE", None)
        or "verse"
    ).strip()


def _openai_tts_timeout_seconds() -> float:
    raw = (
        getattr(settings, "LANGUAGE_OPENAI_TTS_TIMEOUT_SECONDS", None)
        or getattr(settings, "SPEAKING_TTS_TIMEOUT_SECONDS", None)
        or 30
    )
    return float(max(5, min(120, int(raw or 30))))


async def _write_openai_speech(text: str, dest: Path) -> bool:
    api_key = (getattr(settings, "OPENAI_API_KEY", None) or "").strip()
    if not api_key:
        return False

    payload = {
        "model": _openai_tts_model(),
        "voice": _openai_tts_voice(),
        "input": text,
        "response_format": _OPENAI_AUDIO_FORMAT,
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    dest.parent.mkdir(parents=True, exist_ok=True)

    last_error: Exception | None = None
    for attempt in range(2):
        try:
            async with httpx.AsyncClient(timeout=_openai_tts_timeout_seconds()) as client:
                response = await client.post(_OPENAI_SPEECH_URL, headers=headers, json=payload)
                if response.status_code == 429 and attempt == 0:
                    await asyncio.sleep(1.2)
                    continue
                response.raise_for_status()
                audio = response.content
            if not audio:
                return False
            dest.write_bytes(audio)
            return dest.exists() and dest.stat().st_size > 0
        except Exception as exc:  # noqa: BLE001 - lesson audio is optional at this boundary
            last_error = exc
            if attempt == 0:
                continue
            logger.warning("OpenAI lesson audio synthesis failed: %s", type(last_error).__name__)
            return False
    return False


async def _synthesize_openai(
    db: AsyncSession,
    *,
    item: LanguageContentItem,
    text: str,
) -> dict | None:
    if not _openai_tts_enabled():
        return None

    voice_source = _OPENAI_SOURCE
    cache_teacher_id: int | None = None
    dest = _audio_dir(item.id) / f"{voice_source}.{_OPENAI_AUDIO_FORMAT}"

    ok = await _write_openai_speech(text, dest)
    if not ok:
        return None

    storage_key = _storage_key(dest)
    public_url = "/uploads/" + storage_key
    row = await _upsert_cache(
        db,
        content_item_id=item.id,
        voice_source=voice_source,
        teacher_id=cache_teacher_id,
        storage_key=storage_key,
        public_url=public_url,
    )
    return _out(row)


async def get_lesson_audio(db: AsyncSession, *, content_item_id: int, teacher_id: int | None = None) -> dict | None:
    cached = await _cache_lookup(db, content_item_id=content_item_id, teacher_id=teacher_id)
    if cached:
        disk_path = Path(settings.UPLOAD_DIR) / cached.audio_storage_key
        if disk_path.exists():
            return _out(cached)
    return await generate_lesson_audio(db, content_item_id=content_item_id, teacher_id=teacher_id)


async def generate_lesson_audio(
    db: AsyncSession, *, content_item_id: int, teacher_id: int | None = None
) -> dict | None:
    item = await db.get(LanguageContentItem, content_item_id)
    if not item:
        return None
    text = _lesson_text(item)
    if not text:
        return None

    supertonic = await _synthesize_supertonic(db, item=item, text=text)
    if supertonic:
        return supertonic

    return await _synthesize_openai(db, item=item, text=text)
