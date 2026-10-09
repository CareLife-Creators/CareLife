"""Add orphanage impact updates and moderated media.

Revision ID: d7f4b2a91c60
Revises: c41d9a7b6e20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d7f4b2a91c60"
down_revision: Union[str, Sequence[str], None] = "c41d9a7b6e20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "impact_updates",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=30),
            server_default="pending_review",
            nullable=False,
        ),
        sa.Column("created_by", sa.String(), nullable=False),
        sa.Column("reviewed_by", sa.String(), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "reviewed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "published_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.CheckConstraint(
            "status IN ('pending_review', 'approved', 'rejected')",
            name="ck_impact_updates_status",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["reviewed_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_impact_updates_org_status_created",
        "impact_updates",
        ["organization_id", "status", "created_at"],
    )

    op.create_table(
        "impact_media",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("update_id", sa.String(), nullable=False),
        sa.Column("storage_key", sa.String(length=100), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("media_type", sa.String(length=10), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "media_type IN ('image', 'video')",
            name="ck_impact_media_type",
        ),
        sa.CheckConstraint(
            "file_size > 0",
            name="ck_impact_media_file_size",
        ),
        sa.ForeignKeyConstraint(
            ["update_id"],
            ["impact_updates.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
    )

    op.create_index(
        "ix_impact_media_update",
        "impact_media",
        ["update_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_impact_media_update", table_name="impact_media")
    op.drop_table("impact_media")
    op.drop_index(
        "ix_impact_updates_org_status_created",
        table_name="impact_updates",
    )
    op.drop_table("impact_updates")