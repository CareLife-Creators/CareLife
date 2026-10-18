"""Create resident profiles for elder-care organizations."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d2b48f7a6c10"
down_revision: Union[str, Sequence[str], None] = "c2f9a1b6d740"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "resident_profiles",
        sa.Column(
            "id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "full_name",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "preferred_name",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "date_of_birth",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "room_number",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "emergency_contact_name",
            sa.String(length=150),
            nullable=True,
        ),
        sa.Column(
            "emergency_contact_phone",
            sa.String(length=30),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'active'"),
            nullable=False,
        ),
        sa.Column(
            "created_by",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "updated_by",
            sa.String(),
            nullable=False,
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
            "status IN ('active', 'inactive')",
            name="ck_resident_profiles_status",
        ),
        sa.CheckConstraint(
            "(emergency_contact_name IS NULL) = "
            "(emergency_contact_phone IS NULL)",
            name="ck_resident_profiles_emergency_contact_pair",
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
            ["updated_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_resident_profiles_org_status_name",
        "resident_profiles",
        ["organization_id", "status", "full_name"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_resident_profiles_org_status_name",
        table_name="resident_profiles",
    )

    op.drop_table("resident_profiles")