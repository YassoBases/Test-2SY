"""Canonical grammar lesson identity and revision persistence."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

JSONB_TYPE = JSON().with_variant(JSONB, "postgresql")
UUID_TYPE = Uuid(as_uuid=True)

GRAMMAR_CANONICAL_REVISION_STATUSES = (
    "draft",
    "generating",
    "validating",
    "reviewable",
    "published",
    "failed",
    "archived",
)
GRAMMAR_CANONICAL_UNIT_KEYS = (
    "blueprint",
    "concept",
    "examples",
    "rules",
    "practice",
    "production",
)
GRAMMAR_CANONICAL_UNIT_ATTEMPT_STATUSES = (
    "pending",
    "generating",
    "validating",
    "accepted",
    "failed",
    "superseded",
)


class GrammarCanonicalLesson(Base):
    """Stable identity for one grammar lesson target and methodology."""

    __tablename__ = "grammar_canonical_lessons"
    __table_args__ = (
        UniqueConstraint(
            "grammar_id",
            "cefr_level",
            "locale",
            "methodology_version",
            name="uq_grammar_canonical_lessons_identity",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    grammar_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    cefr_level: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    locale: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    methodology_version: Mapped[str] = mapped_column(String(96), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    revisions: Mapped[list["GrammarCanonicalLessonRevision"]] = relationship(
        back_populates="lesson",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class GrammarCanonicalLessonRevision(Base):
    """Versioned canonical educational payload for a grammar lesson identity."""

    __tablename__ = "grammar_canonical_lesson_revisions"
    __table_args__ = (
        UniqueConstraint(
            "lesson_id",
            "revision_number",
            name="uq_grammar_canonical_lesson_revisions_number",
        ),
        CheckConstraint(
            "status IN ("
            "'draft', 'generating', 'validating', 'reviewable', "
            "'published', 'failed', 'archived'"
            ")",
            name="ck_grammar_canonical_lesson_revisions_status",
        ),
        Index(
            "uq_grammar_canonical_lesson_revisions_one_published",
            "lesson_id",
            unique=True,
            postgresql_where=text("status = 'published'"),
            sqlite_where=text("status = 'published'"),
        ),
        Index(
            "ix_grammar_canonical_lesson_revisions_lesson_status",
            "lesson_id",
            "status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey("grammar_canonical_lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft", server_default="draft")
    student_content_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB_TYPE, nullable=True)
    server_teaching_metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB_TYPE, nullable=True)
    schema_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    catalog_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    authoring_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    authoring_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    diagnostics_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB_TYPE, nullable=True)
    raw_artifact_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    lesson: Mapped[GrammarCanonicalLesson] = relationship(back_populates="revisions")
    unit_attempts: Mapped[list["GrammarCanonicalLessonRevisionUnitAttempt"]] = relationship(
        back_populates="revision",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class GrammarCanonicalLessonRevisionUnitAttempt(Base):
    """One blueprint/unit authoring attempt for a canonical lesson revision."""

    __tablename__ = "grammar_canonical_lesson_revision_unit_attempts"
    __table_args__ = (
        UniqueConstraint(
            "revision_id",
            "unit_key",
            "attempt_number",
            name="uq_grammar_canonical_lesson_unit_attempts_number",
        ),
        CheckConstraint(
            "unit_key IN ('blueprint', 'concept', 'examples', 'rules', 'practice', 'production')",
            name="ck_grammar_canonical_lesson_unit_attempts_unit_key",
        ),
        CheckConstraint(
            "status IN ('pending', 'generating', 'validating', 'accepted', 'failed', 'superseded')",
            name="ck_grammar_canonical_lesson_unit_attempts_status",
        ),
        Index(
            "uq_grammar_canonical_lesson_unit_attempts_one_accepted",
            "revision_id",
            "unit_key",
            unique=True,
            postgresql_where=text("status = 'accepted'"),
            sqlite_where=text("status = 'accepted'"),
        ),
        Index(
            "ix_grammar_canonical_lesson_unit_attempts_revision_unit_status",
            "revision_id",
            "unit_key",
            "status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID_TYPE, primary_key=True, default=uuid.uuid4)
    revision_id: Mapped[uuid.UUID] = mapped_column(
        UUID_TYPE,
        ForeignKey("grammar_canonical_lesson_revisions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    unit_key: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", server_default="pending")
    public_payload_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB_TYPE, nullable=True)
    private_metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB_TYPE, nullable=True)
    blueprint_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB_TYPE, nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    stop_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    truncated: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    diagnostics_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB_TYPE, nullable=True)
    raw_artifact_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    revision: Mapped[GrammarCanonicalLessonRevision] = relationship(back_populates="unit_attempts")
