"""Add staff role requests after the current consolidated migration head."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f84c2a1d7b90"
down_revision: Union[str, Sequence[str], None] = "c6a91b3e5d20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_role_requests",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("requested_role", sa.String(length=50), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", sa.String(), nullable=True),
        sa.CheckConstraint(
            "requested_role IN ('daycare_staff', 'orphanage_staff', 'care_home_staff')",
            name="ck_user_role_requests_requested_role",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="ck_user_role_requests_status",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["reviewed_by"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_user_role_requests_user_created",
        "user_role_requests",
        ["user_id", "created_at"],
    )
    op.create_index(
        "uq_user_role_requests_one_pending_per_user",
        "user_role_requests",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("status = 'pending'"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_user_role_requests_one_pending_per_user",
        table_name="user_role_requests",
    )
    op.drop_index(
        "ix_user_role_requests_user_created",
        table_name="user_role_requests",
    )
    op.drop_table("user_role_requests")
