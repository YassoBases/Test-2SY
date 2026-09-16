"""Provider-agnostic media storage — local disk today, Supabase when configured (A6.0)."""

from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.media import MediaAccessScope, MediaObject, MediaStatus, StorageProvider
from app.services.media_storage.constants import (
    PRIVATE_BUCKET,
    PUBLIC_BUCKET,
    bucket_for_access_scope,
    normalize_storage_key,
)
from app.services.media_storage.config import effective_storage_provider

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
    storage_bucket: str | None = None,
    access_scope: str | None = None,
    status: str = MediaStatus.ready.value,
    metadata_json: dict | None = None,
    checksum_sha256: str | None = None,
) -> MediaObject:
    """Persist media metadata; binary already on disk or uploaded to cloud separately."""
    # Keep local as the safe default until upload flows are converted (later A6).
    # Callers opt into supabase by passing storage_provider=StorageProvider.supabase.value.
    provider = (storage_provider or StorageProvider.local.value).strip().lower()
    if provider == StorageProvider.supabase.value and effective_storage_provider() != StorageProvider.supabase.value:
        # Misconfigured supabase → refuse silent metadata-only supabase rows; stay local.
        provider = StorageProvider.local.value
    key = normalize_storage_key(storage_key or storage_path)
    scope = (access_scope or MediaAccessScope.legacy_public.value).strip().lower()

    bucket = storage_bucket
    public_url: str | None
    if provider == StorageProvider.supabase.value:
        bucket = (bucket or bucket_for_access_scope(scope)).strip()
        # Do not persist a permanent public URL for private supabase objects.
        if scope == MediaAccessScope.public.value and bucket == PUBLIC_BUCKET:
            public_url = None  # resolved at download time via public object URL
        else:
            public_url = None
            if not bucket:
                bucket = PRIVATE_BUCKET
    else:
        public_url = _public_url_for_path(storage_path)
        bucket = None

    media = MediaObject(
        storage_provider=provider,
        storage_key=key,
        storage_bucket=bucket,
        public_url=public_url,
        access_scope=scope,
        status=status,
        mime_type=mime_type,
        file_size_bytes=file_size_bytes,
        original_filename=original_filename,
        uploaded_by_user_id=uploaded_by_user_id,
        metadata_json=metadata_json,
        checksum_sha256=checksum_sha256,
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
