"""create child and orphanage outcome tables

Revision ID: b4e0a2c71f55
Revises: a66dca08b27f
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b4e0a2c71f55"
down_revision: Union[str, Sequence[str], None] = "a66dca08b27f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "children",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("parent_id", sa.String(), nullable=True),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("gender", sa.String(length=30), nullable=True),
        sa.Column("allergies", sa.Text(), nullable=True),
        sa.Column("medical_notes", sa.Text(), nullable=True),
        sa.Column("orphanage_organization_id", sa.String(), nullable=True),
        sa.Column("daycare_organization_id", sa.String(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["orphanage_organization_id"],
            ["organizations.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["daycare_organization_id"],
            ["organizations.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "orphanage_outcomes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("child_id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("outcome_type", sa.String(length=30), nullable=False),
        sa.Column("outcome_status", sa.String(length=30), nullable=False),
        sa.Column("outcome_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(), nullable=False),
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
            "outcome_type IN ('adoption', 'guardianship')",
            name="ck_outcome_type",
        ),
        sa.CheckConstraint(
            "outcome_status IN ('pending', 'approved', 'completed', 'cancelled')",
            name="ck_outcome_status",
        ),
        sa.ForeignKeyConstraint(
            ["child_id"],
            ["children.id"],
            ondelete="CASCADE",
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
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_children_orphanage",
        "children",
        ["orphanage_organization_id"],
    )

    op.create_index(
        "ix_outcomes_child",
        "orphanage_outcomes",
        ["child_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_outcomes_child", table_name="orphanage_outcomes")
    op.drop_index("ix_children_orphanage", table_name="children")
    op.drop_table("orphanage_outcomes")
    op.drop_table("children")
                                                                                                                    