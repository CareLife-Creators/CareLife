"""Add resident family consent and remote check-in tables."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f17b3a9c2d41"
down_revision: Union[str, Sequence[str], None] = "b7d4e9a2c681"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "resident_family_consents",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("resident_id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column(
            "family_representative_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("granted_by", sa.String(), nullable=True),
        sa.Column(
            "granted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("revoked_by", sa.String(), nullable=True),
        sa.Column(
            "revoked_at",
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
            "status IN ('active', 'revoked')",
            name="ck_resident_family_consents_status",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["family_representative_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["granted_by"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["revoked_by"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "resident_id",
            "organization_id",
            "family_representative_id",
            name="uq_resident_family_consent",
        ),
    )

    op.create_index(
        "ix_resident_family_consents_resident",
        "resident_family_consents",
        ["resident_id", "status"],
    )

    op.create_table(
        "resident_remote_checkins",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("consent_id", sa.String(), nullable=False),
        sa.Column("resident_id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("actor_user_id", sa.String(), nullable=False),
        sa.Column(
            "wellbeing_status",
            sa.String(30),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "wellbeing_status IN "
            "('well', 'needs_attention', 'urgent')",
            name="ck_remote_checkins_wellbeing_status",
        ),
        sa.ForeignKeyConstraint(
            ["consent_id"],
            ["resident_family_consents.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_remote_checkins_resident_recorded",
        "resident_remote_checkins",
        ["resident_id", "recorded_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_remote_checkins_resident_recorded",
        table_name="resident_remote_checkins",
    )
    op.drop_table("resident_remote_checkins")

    op.drop_index(
        "ix_resident_family_consents_resident",
        table_name="resident_family_consents",
    )
    op.drop_table("resident_family_consents")