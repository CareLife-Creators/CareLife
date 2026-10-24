"""Add resident-linked elder-care bookings and status history."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c6a91b3e5d20"
down_revision: Union[str, Sequence[str], None] = "b2e7d4a9c613"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "elder_care_bookings",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("resident_id", sa.String(), nullable=False),
        sa.Column("requester_user_id", sa.String(), nullable=False),
        sa.Column(
            "provider_type",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "caregiver_user_id",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "organization_id",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "availability_id",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "service_type",
            sa.String(length=100),
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
        sa.Column("decision_message", sa.Text(), nullable=True),
        sa.Column("reviewed_by", sa.String(), nullable=True),
        sa.Column(
            "reviewed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("cancelled_by", sa.String(), nullable=True),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "ends_at > starts_at",
            name="ck_elder_care_bookings_time_range",
        ),
        sa.CheckConstraint(
            "status IN "
            "('requested', 'approved', 'rejected', "
            "'cancelled', 'completed')",
            name="ck_elder_care_bookings_status",
        ),
        sa.CheckConstraint(
            "(provider_type = 'caregiver' "
            "AND caregiver_user_id IS NOT NULL "
            "AND organization_id IS NULL "
            "AND availability_id IS NOT NULL) "
            "OR "
            "(provider_type = 'care_home' "
            "AND caregiver_user_id IS NULL "
            "AND organization_id IS NOT NULL "
            "AND availability_id IS NULL)",
            name="ck_elder_care_bookings_provider",
        ),
        sa.ForeignKeyConstraint(
            ["resident_id"],
            ["resident_profiles.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["requester_user_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["caregiver_user_id"],
            ["caregiver_profiles.user_id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["availability_id"],
            ["caregiver_availability.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["reviewed_by"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["cancelled_by"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_elder_care_bookings_resident_start",
        "elder_care_bookings",
        ["resident_id", "starts_at"],
    )

    op.create_index(
        "ix_elder_care_bookings_caregiver_status_start",
        "elder_care_bookings",
        ["caregiver_user_id", "status", "starts_at"],
    )

    op.create_index(
        "ix_elder_care_bookings_organization_status_start",
        "elder_care_bookings",
        ["organization_id", "status", "starts_at"],
    )

    op.create_index(
        "ix_elder_care_bookings_requester_created",
        "elder_care_bookings",
        ["requester_user_id", "created_at"],
    )

    op.create_table(
        "elder_care_booking_status_history",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("booking_id", sa.String(), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=False),
        sa.Column(
            "from_status",
            sa.String(length=20),
            nullable=True,
        ),
        sa.Column(
            "to_status",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column("changed_by", sa.String(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "to_status IN "
            "('requested', 'approved', 'rejected', "
            "'cancelled', 'completed')",
            name="ck_elder_care_booking_history_to_status",
        ),
        sa.CheckConstraint(
            "from_status IS NULL OR from_status IN "
            "('requested', 'approved', 'rejected', "
            "'cancelled', 'completed')",
            name="ck_elder_care_booking_history_from_status",
        ),
        sa.ForeignKeyConstraint(
            ["booking_id"],
            ["elder_care_bookings.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["changed_by"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "booking_id",
            "sequence_no",
            name="uq_elder_care_booking_history_sequence",
        ),
    )


def downgrade() -> None:
    op.drop_table("elder_care_booking_status_history")

    op.drop_index(
        "ix_elder_care_bookings_requester_created",
        table_name="elder_care_bookings",
    )

    op.drop_index(
        "ix_elder_care_bookings_organization_status_start",
        table_name="elder_care_bookings",
    )

    op.drop_index(
        "ix_elder_care_bookings_caregiver_status_start",
        table_name="elder_care_bookings",
    )

    op.drop_index(
        "ix_elder_care_bookings_resident_start",
        table_name="elder_care_bookings",
    )

    op.drop_table("elder_care_bookings")