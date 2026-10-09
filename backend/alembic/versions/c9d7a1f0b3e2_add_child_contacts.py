"""add child contacts table

Revision ID: c9d7a1f0b3e2
Revises: b4e0a2c71f55
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c9d7a1f0b3e2"
down_revision: Union[str, Sequence[str], None] = "b4e0a2c71f55"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "child_contacts",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("child_id", sa.String(), nullable=False),
        sa.Column(
            "contact_type",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "full_name",
            sa.String(length=200),
            nullable=False,
        ),
        sa.Column(
            "relationship_to_child",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "phone",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=254),
            nullable=True,
        ),
        sa.Column(
            "address",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "created_by",
            sa.String(),
            nullable=False,
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
            "contact_type IN ('emergency', 'pickup')",
            name="ck_child_contact_type",
        ),
        sa.ForeignKeyConstraint(
            ["child_id"],
            ["children.id"],
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
        "ix_child_contacts_child_type",
        "child_contacts",
        ["child_id", "contact_type"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_child_contacts_child_type",
        table_name="child_contacts",
    )

    op.drop_table("child_contacts")