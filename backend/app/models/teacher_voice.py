"""Teacher voice sample for AI persona + TTS (not exposed to students)."""

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class VoiceSampleStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    awaiting_acceptance = "awaiting_acceptance"
    ready = "ready"
    failed = "failed"


class TeacherVoiceSample(Base):
    __tablename__ = "teacher_voice_samples"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    teacher_profile_id: Mapped[int] = mapped_column(
        ForeignKey("teacher_profiles.id", ondelete="CASCADE"), index=True
    )
    storage_path: Mapped[str] = mapped_column(String(1024))
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    processing_status: Mapped[str] = mapped_column(String(32), default=VoiceSampleStatus.pending.value)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    persona_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    elevenlabs_voice_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    elevenlabs_requires_verification: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_tier: Mapped[str | None] = mapped_column(String(32), nullable=True)
    clone_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    transcript_quality: Mapped[float | None] = mapped_column(Float, nullable=True)
    noise_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    speech_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    preview_audio_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    teacher_accepted: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    quality_details_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    teacher_profile: Mapped["TeacherProfile"] = relationship(back_populates="voice_samples")
