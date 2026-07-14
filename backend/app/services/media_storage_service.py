"""Provider-agnostic media storage — local disk today, S3/R2/MinIO later."""

from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.media import MediaObject, StorageProvider

settings = get_settings()


def _public_url_for_path(storage_path: str) -> str:
    p = storage_path.replace("\\", "/")
    if p.startswith("/uploads/"):
        return p
    if p.startswith("uploads/"):
        return "/" + p
    return "/uploads/" + p.lstrip("/")


async def register_media_object(
    db: AsyncSession,
    *,
    storage_path: str,
    mime_type: str | None = None,
    file_size_bytes: int | None = None,
    original_filename: str | None = None,
    uploaded_by_user_id: int | None = None,
    storage_provider: str = StorageProvider.local.value,
    storage_key: str | None = None,
) -> MediaObject:
    """Persist media metadata; binary already on disk or uploaded to cloud separately."""
    key = storage_key or storage_path
    media = MediaObject(
        storage_provider=storage_provider,
        storage_key=key,
        public_url=_public_url_for_path(storage_path),
        mime_type=mime_type,
        file_size_bytes=file_size_bytes,
        original_filename=original_filename,
        uploaded_by_user_id=uploaded_by_user_id,
    )
    db.add(media)
    await db.flush()
    return media


def save_local_file(
    *,
    user_id: int,
    category: str,
    content: bytes,
    filename: str,
) -> tuple[str, str]:
    """Write bytes under UPLOAD_DIR and return (absolute_path, public_url)."""
    ext = Path(filename).suffix or ""
    root = Path(settings.UPLOAD_DIR) / f"teacher_{user_id}" / category
    root.mkdir(parents=True, exist_ok=True)
    dest = root / f"{uuid.uuid4().hex}{ext}"
    dest.write_bytes(content)
    rel = dest.resolve().relative_to(Path(settings.UPLOAD_DIR).resolve())
    public = "/uploads/" + "/".join(rel.parts)
    return str(dest), public
