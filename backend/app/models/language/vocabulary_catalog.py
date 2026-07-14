"""Offline vocabulary catalog — a global, LLM-free reference of words for the infinite generator.

`LanguageVocabularyCatalog` is shared reference data (word + metadata). `LanguageVocabularyCatalogSeen`
tracks which catalog words a student has already been served, so the generator never repeats a word
for that learner (zero duplication). Integer keys (module convention).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LanguageVocabularyCatalog(Base):
    __tablename__ = "language_vocabulary_catalog"
    __table_args__ = (
        UniqueConstraint("word", "cefr_level", name="uq_language_vocabulary_catalog_word_level"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    word: Mapped[str] = mapped_column(String(80), index=True)
    part_of_speech: Mapped[str] = mapped_column(String(40), default="", server_default="")
    translation: Mapped[str] = mapped_column(String(200), default="", server_default="")  # e.g. Arabic
    definition: Mapped[str] = mapped_column(Text, default="", server_default="")
    context_theme: Mapped[str] = mapped_column(String(60), default="", server_default="", index=True)
    example_sentence: Mapped[str] = mapped_column(Text, default="", server_default="")
    cefr_level: Mapped[str] = mapped_column(String(4), default="", server_default="", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LanguageVocabularyCatalogSeen(Base):
    __tablename__ = "language_vocabulary_catalog_seen"
    __table_args__ = (
        UniqueConstraint("student_id", "catalog_id", name="uq_language_vocabulary_catalog_seen"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    catalog_id: Mapped[int] = mapped_column(
        ForeignKey("language_vocabulary_catalog.id", ondelete="CASCADE"), index=True
    )
    seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
