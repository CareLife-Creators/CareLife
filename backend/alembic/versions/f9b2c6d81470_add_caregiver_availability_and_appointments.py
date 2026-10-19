"""Add independent caregiver availability and appointments."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f9b2c6d81470"

down_revision: Union[str, Sequence[str], None] = (
    "a5f7c9d2e4b1"
)

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "caregiver_availability",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column(
            "caregiver_user_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "starts_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "ends_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "ends_at > starts_at",
            name="ck_caregiver_availability_time_range",
        ),
        sa.ForeignKeyConstraint(
            ["caregiver_user_id"],
            ["caregiver_profiles.user_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_caregiver_availability_caregiver_start",
        "caregiver_availability",
        ["caregiver_user_id", "starts_at"],
    )

    op.create_table(
        "caregiver_appointments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column(
            "availability_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "caregiver_user_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "requester_user_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "service_type",
            sa.String(length=40),
            nullable=False,
        ),
        sa.Column(
            "starts_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "ends_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'requested'"),
            nullable=False,
        ),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column(
            "decision_message",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "reviewed_by",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "reviewed_at",
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
            "ends_at > starts_at",
            name="ck_caregiver_appointments_time_range",
        ),
        sa.CheckConstraint(
            "status IN ('requested', 'accepted', 'rejected')",
            name="ck_caregiver_appointments_status",
        ),
        sa.ForeignKeyConstraint(
            ["availability_id"],
            ["caregiver_availability.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["caregiver_user_id"],
            ["caregiver_profiles.user_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["requester_user_id"],
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
        "ix_caregiver_appointments_requester",
        "caregiver_appointments",
        ["requester_user_id", "created_at"],
    )

    op.create_index(
        "ix_caregiver_appointments_caregiver",
        "caregiver_appointments",
        ["caregiver_user_id", "starts_at"],
    )

    # One availability slot cannot have multiple active bookings.
    # A rejected appointment releases the slot.
    op.create_index(
        "uq_caregiver_appointment_active_slot",
        "caregiver_appointments",
        ["availability_id"],
        unique=True,
        postgresql_where=sa.text(
            "status IN ('requested', 'accepted')"
        ),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_caregiver_appointment_active_slot",
        table_name="caregiver_appointments",
    )

    op.drop_index(
        "ix_caregiver_appointments_caregiver",
        table_name="caregiver_appointments",
    )

    op.drop_index(
        "ix_caregiver_appointments_requester",
        table_name="caregiver_appointments",
    )

    op.drop_table("caregiver_appointments")

    op.drop_index(
        "ix_caregiver_availability_caregiver_start",
        table_name="caregiver_availability",
    )

    op.drop_table("caregiver_availability")