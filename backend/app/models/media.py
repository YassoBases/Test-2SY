"""Provider-agnostic media metadata — blobs live in S3/R2/MinIO/local disk."""

import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StorageProvider(str, enum.Enum):
    local = "local"
    s3 = "s3"
    r2 = "r2"
    minio = "minio"


class MediaObject(Base):
    __tablename__ = "media_objects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    storage_provider: Mapped[str] = mapped_column(String(32), default=StorageProvider.local.value, index=True)
    storage_key: Mapped[str] = mapped_column(String(1024), index=True)
    public_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    original_filename: Mapped[str | None] = mapped_column(String(500), nullable=True)
    uploaded_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
