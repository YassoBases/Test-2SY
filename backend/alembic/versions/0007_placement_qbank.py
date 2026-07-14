"""Placement question bank foundation.

Revision ID: 0007_placement_qbank
Revises: 0006_language_listening_reservations
Create Date: 2026-07-07
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0007_placement_qbank"
down_revision = "0006_language_listening_reservations"
branch_labels = None
depends_on = None


language_level = postgresql.ENUM("A1", "A2", "B1", "B2", "C1", "C2", name="language_level", create_type=False)


def upgrade() -> None:
    op.create_table(
        "language_placement_question_bank_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("language_id", sa.Integer(), nullable=False),
        sa.Column("skill", sa.String(length=32), nullable=False),
        sa.Column("level", language_level, nullable=False),
        sa.Column("boundary_low_level", language_level, nullable=True),
        sa.Column("boundary_high_level", language_level, nullable=True),
        sa.Column("subskill", sa.String(length=64), nullable=True),
        sa.Column("question_type", sa.String(length=32), server_default="mcq", nullable=False),
        sa.Column("prompt_text", sa.Text(), nullable=False),
        sa.Column("passage", sa.Text(), nullable=True),
        sa.Column("situation", sa.Text(), nullable=True),
        sa.Column("options_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("correct_index", sa.Integer(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("media_object_id", sa.Integer(), nullable=True),
        sa.Column("audio_meta_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("body_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("stable_key", sa.String(length=160), nullable=True),
        sa.Column("source", sa.String(length=32), server_default="ai_generated", nullable=False),
        sa.Column("is_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("reviewer_note", sa.Text(), nullable=True),
        sa.Column("usage_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("correct_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("difficulty_estimate", sa.Float(), nullable=True),
        sa.Column("discrimination_estimate", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["language_id"], ["languages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["media_object_id"], ["media_objects.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stable_key"),
    )
    op.create_index(
        "ix_lpq_bank_boundary",
        "language_placement_question_bank_items",
        ["language_id", "skill", "boundary_low_level", "boundary_high_level", "is_verified", "is_active"],
    )
    op.create_index(
        "ix_lpq_bank_lookup",
        "language_placement_question_bank_items",
        ["language_id", "skill", "level", "is_verified", "is_active"],
    )
    op.create_index(
        "ix_language_placement_question_bank_items_language_id",
        "language_placement_question_bank_items",
        ["language_id"],
    )
    op.create_index(
        "ix_language_placement_question_bank_items_level",
        "language_placement_question_bank_items",
        ["level"],
    )
    op.create_index(
        "ix_language_placement_question_bank_items_skill",
        "language_placement_question_bank_items",
        ["skill"],
    )
    op.create_index(
        "ix_language_placement_question_bank_items_subskill",
        "language_placement_question_bank_items",
        ["subskill"],
    )


def downgrade() -> None:
    op.drop_index("ix_language_placement_question_bank_items_subskill", table_name="language_placement_question_bank_items")
    op.drop_index("ix_language_placement_question_bank_items_skill", table_name="language_placement_question_bank_items")
    op.drop_index("ix_language_placement_question_bank_items_level", table_name="language_placement_question_bank_items")
    op.drop_index("ix_language_placement_question_bank_items_language_id", table_name="language_placement_question_bank_items")
    op.drop_index("ix_lpq_bank_lookup", table_name="language_placement_question_bank_items")
    op.drop_index("ix_lpq_bank_boundary", table_name="language_placement_question_bank_items")
    op.drop_table("language_placement_question_bank_items")
