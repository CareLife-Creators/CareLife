"""Add in-kind donation pledges.

Revision ID: c2f9a1b6d740
Revises: f17b3a9c2d41
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c2f9a1b6d740"
down_revision: Union[str, Sequence[str], None] = "f17b3a9c2d41"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "in_kind_donation_pledges",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("need_id", sa.String(), nullable=False),
        sa.Column("donor_id", sa.String(), nullable=False),
        sa.Column(
            "quantity",
            sa.Numeric(precision=12, scale=3),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'pledged'"),
            nullable=False,
        ),
        sa.Column("received_by", sa.String(), nullable=True),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("allocated_by", sa.String(), nullable=True),
        sa.Column(
            "allocated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
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
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_in_kind_pledges_quantity_positive",
        ),
        sa.CheckConstraint(
            "status IN ('pledged', 'received', 'allocated')",
            name="ck_in_kind_pledges_status",
        ),
        sa.CheckConstraint(
            "(status = 'pledged' "
            "AND received_at IS NULL AND allocated_at IS NULL) "
            "OR (status = 'received' "
            "AND received_at IS NOT NULL AND allocated_at IS NULL) "
            "OR (status = 'allocated' "
            "AND received_at IS NOT NULL AND allocated_at IS NOT NULL)",
            name="ck_in_kind_pledges_status_timestamps",
        ),
        sa.ForeignKeyConstraint(
            ["need_id"],
            ["donation_needs.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["donor_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["received_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["allocated_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_in_kind_pledges_donor_created",
        "in_kind_donation_pledges",
        ["donor_id", "created_at"],
    )

    op.create_index(
        "ix_in_kind_pledges_need_status_created",
        "in_kind_donation_pledges",
        ["need_id", "status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_in_kind_pledges_need_status_created",
        table_name="in_kind_donation_pledges",
    )

    op.drop_index(
        "ix_in_kind_pledges_donor_created",
        table_name="in_kind_donation_pledges",
    )

    op.drop_table("in_kind_donation_pledges")