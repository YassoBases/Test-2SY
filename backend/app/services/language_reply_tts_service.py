"""English reply TTS for language AI conversations via Supertonic."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.media import MediaObject, StorageProvider
from app.services.language_supertonic_service import (
    language_tts_audio_extension,
    language_tts_audio_mime_type,
    synthesize_language_speech,
)
from app.services.media_storage_service import register_media_object

logger = logging.getLogger(__name__)
settings = get_settings()


async def synthesize_english_reply(
    db: AsyncSession,
    *,
    student_id: int,
    text: str,
) -> MediaObject | None:
    """Generate English reply audio. Returns None when language TTS is disabled or unavailable."""
    cleaned = (text or "").strip()
    if not cleaned:
        return None

    if not settings.ENABLE_TTS:
        logger.info("ENABLE_TTS=false - skipping language conversation reply audio")
        return None

    upload_dir = Path(settings.UPLOAD_DIR) / f"student_{student_id}" / "language_conversation"
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"reply_{uuid.uuid4().hex}{language_tts_audio_extension()}"
    dest = upload_dir / filename

    ok = await synthesize_language_speech(
        cleaned,
        language="en",
        output_path=dest,
    )
    if not ok or not dest.exists():
        logger.warning("Language conversation reply TTS failed (continuing without audio)")
        if dest.exists():
            dest.unlink(missing_ok=True)
        return None

    rel = dest.resolve().relative_to(Path(settings.UPLOAD_DIR).resolve())
    storage_key = "/".join(rel.parts)
    media = await register_media_object(
        db,
        storage_path="uploads/" + storage_key,
        mime_type=language_tts_audio_mime_type(),
        file_size_bytes=dest.stat().st_size,
        original_filename=filename,
        uploaded_by_user_id=student_id,
        storage_provider=StorageProvider.local.value,
        storage_key=storage_key,
    )
    media.public_url = "/uploads/" + storage_key
    return media
