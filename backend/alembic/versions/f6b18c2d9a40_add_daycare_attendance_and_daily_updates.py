"""Add daycare attendance and daily updates.

Revision ID: f6b18c2d9a40
Revises: d1e4f6a8b2c0
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f6b18c2d9a40"
down_revision: Union[str, Sequence[str], None] = "d1e4f6a8b2c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "daycare_attendance",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("enrollment_id", sa.String(), nullable=False),
        sa.Column("attendance_date", sa.Date(), nullable=False),
        sa.Column(
            "check_in_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "check_out_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("recorded_by", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["enrollment_id"],
            ["daycare_enrollments.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["recorded_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "enrollment_id",
            "attendance_date",
            name="uq_daycare_attendance_enrollment_date",
        ),
        sa.CheckConstraint(
            "check_out_at IS NULL OR check_out_at >= check_in_at",
            name="ck_daycare_attendance_checkout_order",
        ),
    )

    op.create_table(
        "daycare_daily_updates",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("child_id", sa.String(), nullable=False),
        sa.Column(
            "daycare_organization_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column("update_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("recorded_by", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["child_id"],
            ["children.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["daycare_organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["recorded_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_daycare_daily_updates_child_date",
        "daycare_daily_updates",
        ["child_id", "update_date"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_daycare_daily_updates_child_date",
        table_name="daycare_daily_updates",
    )

    op.drop_table("daycare_daily_updates")
    op.drop_table("daycare_attendance")