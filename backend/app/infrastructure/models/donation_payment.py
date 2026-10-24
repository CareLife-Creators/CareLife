from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base


class DonationPaymentModel(Base):
    __tablename__ = "donation_payments"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    campaign_id: Mapped[str] = mapped_column(
        ForeignKey(
            "donation_campaigns.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    donor_user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        server_default=text("'BDT'"),
    )

    payment_method: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'bkash'"),
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'pending'"),
    )

    merchant_invoice_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    bkash_payment_id: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    bkash_transaction_id: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    provider_status: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    failure_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_donation_payments_amount_positive",
        ),
        CheckConstraint(
            "currency = 'BDT'",
            name="ck_donation_payments_currency_bdt",
        ),
        CheckConstraint(
            "payment_method = 'bkash'",
            name="ck_donation_payments_method_bkash",
        ),
        CheckConstraint(
            "status IN ('pending', 'paid', 'failed', 'cancelled')",
            name="ck_donation_payments_status",
        ),
        UniqueConstraint(
            "merchant_invoice_number",
            name="uq_donation_payments_invoice",
        ),
        UniqueConstraint(
            "bkash_payment_id",
            name="uq_donation_payments_bkash_id",
        ),
        UniqueConstraint(
            "bkash_transaction_id",
            name="uq_donation_payments_bkash_trx",
        ),
        Index(
            "ix_donation_payments_donor_created",
            "donor_user_id",
            "created_at",
        ),
        Index(
            "ix_donation_payments_campaign_status",
            "campaign_id",
            "status",
        ),
    )