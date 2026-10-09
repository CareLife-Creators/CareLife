
"""Add caregiver profiles and submitted documents."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b8c2d4e6f901"
down_revision: Union[str, Sequence[str], None] = "c41d9a7b6e20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "caregiver_profiles",
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("service_type", sa.String(length=40), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column(
            "experience_years",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column(
            "verification_status",
            sa.String(length=20),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column("review_message", sa.Text(), nullable=True),
        sa.Column("reviewed_by", sa.String(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
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
            "service_type IN ('nanny', 'elder_care_giver')",
            name="ck_caregiver_profiles_service_type",
        ),
        sa.CheckConstraint(
            "experience_years >= 0",
            name="ck_caregiver_profiles_experience_years",
        ),
        sa.CheckConstraint(
            "verification_status IN ('pending', 'approved', 'rejected')",
            name="ck_caregiver_profiles_verification_status",
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
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_table(
        "caregiver_documents",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("caregiver_user_id", sa.String(), nullable=False),
        sa.Column("document_type", sa.String(length=30), nullable=False),
        sa.Column("document_reference", sa.Text(), nullable=False),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "document_type IN ('identity', 'qualification')",
            name="ck_caregiver_documents_type",
        ),
        sa.ForeignKeyConstraint(
            ["caregiver_user_id"],
            ["caregiver_profiles.user_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_caregiver_documents_user",
        "caregiver_documents",
        ["caregiver_user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_caregiver_documents_user",
        table_name="caregiver_documents",
    )

    op.drop_table("caregiver_documents")
    op.drop_table("caregiver_profiles")