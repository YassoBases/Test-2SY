"""Multi-asset lessons: video + PDF + homework on one lesson row."""

from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.models.lesson import Lesson, LessonAsset, LessonAssetType

settings = get_settings()


def public_url(path: str | None) -> str | None:
    if not path:
        return None
    if path.startswith("http") or path.startswith("/uploads/"):
        return path
    try:
        rel = Path(path).resolve().relative_to(Path(settings.UPLOAD_DIR).resolve())
        return "/uploads/" + "/".join(rel.parts)
    except Exception:
        return None


def asset_map_from_lesson(lesson: Lesson) -> dict[str, LessonAsset]:
    """Build type → asset from relationship or legacy columns."""
    out: dict[str, LessonAsset] = {}
    if "assets" in inspect(lesson).unloaded:
        return out
    for asset in lesson.assets or []:
        t = asset.asset_type.value if hasattr(asset.asset_type, "value") else str(asset.asset_type)
        out[t] = asset
    return out


def paths_from_lesson(lesson: Lesson) -> dict[str, str | None]:
    """Resolved storage paths: video, pdf, homework, audio."""
    amap = asset_map_from_lesson(lesson)
    video = amap.get(LessonAssetType.video.value)
    pdf = amap.get(LessonAssetType.pdf.value)
    hw = amap.get(LessonAssetType.homework.value)
    audio = amap.get(LessonAssetType.audio.value)
    return {
        "video": video.storage_path if video else lesson.video_url,
        "pdf": pdf.storage_path if pdf else lesson.pdf_path,
        "homework": hw.storage_path if hw else lesson.homework_path,
        "audio": audio.storage_path if audio else lesson.voice_path,
    }


def sync_lesson_legacy_columns(lesson: Lesson) -> None:
    """Keep legacy columns in sync for existing AI/upload code."""
    paths = paths_from_lesson(lesson)
    lesson.video_url = paths["video"]
    lesson.pdf_path = paths["pdf"]
    lesson.homework_path = paths["homework"]


async def load_lesson_with_assets(db: AsyncSession, lesson_id: int) -> Lesson | None:
    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id).options(selectinload(Lesson.assets))
    )
    lesson = result.scalar_one_or_none()
    if lesson:
        sync_lesson_legacy_columns(lesson)
    return lesson


def _sync_legacy_column_for_asset(lesson: Lesson, asset_type: LessonAssetType, storage_path: str) -> None:
    """Update legacy path columns without lazy-loading lesson.assets (async-safe)."""
    if asset_type == LessonAssetType.video:
        lesson.video_url = storage_path
    elif asset_type == LessonAssetType.pdf:
        lesson.pdf_path = storage_path
    elif asset_type == LessonAssetType.homework:
        lesson.homework_path = storage_path
    elif asset_type == LessonAssetType.audio:
        lesson.voice_path = storage_path


async def upsert_asset(
    db: AsyncSession,
    lesson: Lesson,
    asset_type: LessonAssetType,
    storage_path: str,
    *,
    original_filename: str | None = None,
    mime_type: str | None = None,
    file_size_bytes: int | None = None,
    uploaded_by_user_id: int | None = None,
) -> LessonAsset:
    from app.services.media_storage_service import register_media_object

    result = await db.execute(
        select(LessonAsset)
        .where(
            LessonAsset.lesson_id == lesson.id,
            LessonAsset.asset_type == asset_type,
        )
        .order_by(LessonAsset.sort_order.desc())
        .limit(1)
    )
    existing = result.scalar_one_or_none()

    media = await register_media_object(
        db,
        storage_path=storage_path,
        mime_type=mime_type,
        file_size_bytes=file_size_bytes,
        original_filename=original_filename,
        uploaded_by_user_id=uploaded_by_user_id,
    )

    if existing:
        existing.storage_path = storage_path
        existing.media_object_id = media.id
        existing.mime_type = mime_type
        existing.file_size_bytes = file_size_bytes
        if original_filename:
            existing.original_filename = original_filename
        asset = existing
    else:
        sort_hint = {"video": 0, "pdf": 1, "homework": 2}.get(asset_type.value, 10)
        asset = LessonAsset(
            lesson_id=lesson.id,
            asset_type=asset_type,
            storage_path=storage_path,
            media_object_id=media.id,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
            original_filename=original_filename,
            sort_order=sort_hint,
        )
        db.add(asset)

    _sync_legacy_column_for_asset(lesson, asset_type, storage_path)
    await db.flush()
    return asset


async def save_lesson_file(
    db: AsyncSession,
    lesson: Lesson,
    asset_type: LessonAssetType,
    content: bytes,
    filename: str,
    *,
    user_id: int,
    course_id: int,
    mime_type: str | None = None,
) -> LessonAsset:
    upload_dir = Path(settings.UPLOAD_DIR) / f"teacher_{user_id}" / f"course_{course_id}"
    upload_dir.mkdir(parents=True, exist_ok=True)
    prefix = asset_type.value
    ext = Path(filename or f"{prefix}.bin").suffix
    if not ext:
        ext = ".mp4" if asset_type == LessonAssetType.video else ".pdf"
    dest = upload_dir / f"{prefix}_{lesson.id}_{uuid.uuid4().hex}{ext}"
    dest.write_bytes(content)
    return await upsert_asset(
        db,
        lesson,
        asset_type,
        str(dest),
        original_filename=filename,
        mime_type=mime_type,
        file_size_bytes=len(content),
        uploaded_by_user_id=user_id,
    )


def lesson_has_any_asset(lesson: Lesson) -> bool:
    paths = paths_from_lesson(lesson)
    return any(paths.values())


def assets_public_urls(lesson: Lesson) -> dict[str, str | None]:
    paths = paths_from_lesson(lesson)
    urls = {k: public_url(v) for k, v in paths.items()}
    return urls


def _clear_legacy_column(lesson: Lesson, asset_type: LessonAssetType) -> None:
    if asset_type == LessonAssetType.video:
        lesson.video_url = None
    elif asset_type == LessonAssetType.pdf:
        lesson.pdf_path = None
    elif asset_type == LessonAssetType.homework:
        lesson.homework_path = None
    elif asset_type == LessonAssetType.audio:
        lesson.voice_path = None


def _safe_unlink(path: str | None) -> None:
    if not path:
        return
    try:
        file_path = Path(path)
        if file_path.is_file():
            file_path.unlink(missing_ok=True)
    except Exception:
        pass


async def remove_lesson_asset(
    db: AsyncSession,
    lesson: Lesson,
    asset_type: LessonAssetType,
) -> None:
    """Remove asset row, clear legacy column, and delete file from disk."""
    amap = asset_map_from_lesson(lesson)
    asset = amap.get(asset_type.value)
    old_path = asset.storage_path if asset else paths_from_lesson(lesson).get(asset_type.value)
    if asset:
        await db.delete(asset)
    _clear_legacy_column(lesson, asset_type)
    _safe_unlink(old_path)
    await db.flush()
