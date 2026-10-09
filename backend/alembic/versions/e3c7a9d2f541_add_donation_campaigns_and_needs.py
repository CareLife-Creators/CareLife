"""Add organization-managed donation campaigns and donation needs.

Revision ID: e3c7a9d2f541
Revises: f6b18c2d9a40
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e3c7a9d2f541"
down_revision: Union[str, Sequence[str], None] = "f6b18c2d9a40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "donation_campaigns",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), server_default="BDT", nullable=False),
        sa.Column("utilized_amount", sa.Numeric(precision=12, scale=2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_by", sa.String(), nullable=False),
        sa.Column("updated_by", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("target_amount > 0", name="ck_donation_campaigns_target_positive"),
        sa.CheckConstraint("utilized_amount >= 0", name="ck_donation_campaigns_utilized_nonnegative"),
        sa.CheckConstraint("length(currency) = 3 AND currency = upper(currency)", name="ck_donation_campaigns_currency_code"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_donation_campaigns_org_active_created",
        "donation_campaigns",
        ["organization_id", "is_active", "created_at"],
    )

    op.create_table(
        "donation_needs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("need_type", sa.String(length=20), nullable=False),
        sa.Column("target_amount", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("target_quantity", sa.Numeric(precision=12, scale=3), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_by", sa.String(), nullable=False),
        sa.Column("updated_by", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("need_type IN ('monetary', 'in_kind')", name="ck_donation_needs_type"),
        sa.CheckConstraint(
            "(need_type = 'monetary' AND target_amount IS NOT NULL AND target_amount > 0 "
            "AND target_quantity IS NULL AND unit IS NULL) "
            "OR (need_type = 'in_kind' AND target_amount IS NULL "
            "AND target_quantity IS NOT NULL AND target_quantity > 0 "
            "AND unit IS NOT NULL AND length(trim(unit)) > 0)",
            name="ck_donation_needs_target_matches_type",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_donation_needs_org_active_created",
        "donation_needs",
        ["organization_id", "is_active", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_donation_needs_org_active_created", table_name="donation_needs")
    op.drop_table("donation_needs")
    op.drop_index("ix_donation_campaigns_org_active_created", table_name="donation_campaigns")
    op.drop_table("donation_campaigns")
