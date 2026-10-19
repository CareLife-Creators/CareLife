"""Add bKash donation payment transactions."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2e7d4a9c613"
down_revision: Union[str, Sequence[str], None] = "5de77978c822"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "donation_payments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("campaign_id", sa.String(), nullable=False),
        sa.Column("donor_user_id", sa.String(), nullable=False),
        sa.Column(
            "amount",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.Column(
            "currency",
            sa.String(length=3),
            server_default=sa.text("'BDT'"),
            nullable=False,
        ),
        sa.Column(
            "payment_method",
            sa.String(length=20),
            server_default=sa.text("'bkash'"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column(
            "merchant_invoice_number",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "bkash_payment_id",
            sa.String(length=150),
            nullable=True,
        ),
        sa.Column(
            "bkash_transaction_id",
            sa.String(length=150),
            nullable=True,
        ),
        sa.Column(
            "provider_status",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "paid_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.CheckConstraint(
            "amount > 0",
            name="ck_donation_payments_amount_positive",
        ),
        sa.CheckConstraint(
            "currency = 'BDT'",
            name="ck_donation_payments_currency_bdt",
        ),
        sa.CheckConstraint(
            "payment_method = 'bkash'",
            name="ck_donation_payments_method_bkash",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'paid', 'failed', 'cancelled')",
            name="ck_donation_payments_status",
        ),
        sa.ForeignKeyConstraint(
            ["campaign_id"],
            ["donation_campaigns.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["donor_user_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "merchant_invoice_number",
            name="uq_donation_payments_invoice",
        ),
        sa.UniqueConstraint(
            "bkash_payment_id",
            name="uq_donation_payments_bkash_id",
        ),
        sa.UniqueConstraint(
            "bkash_transaction_id",
            name="uq_donation_payments_bkash_trx",
        ),
    )

    op.create_index(
        "ix_donation_payments_donor_created",
        "donation_payments",
        ["donor_user_id", "created_at"],
    )

    op.create_index(
        "ix_donation_payments_campaign_status",
        "donation_payments",
        ["campaign_id", "status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_donation_payments_campaign_status",
        table_name="donation_payments",
    )

    op.drop_index(
        "ix_donation_payments_donor_created",
        table_name="donation_payments",
    )

    op.drop_table("donation_payments")