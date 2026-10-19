from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel


class DonationPaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DonationPayment(BaseModel):
    id: str
    campaign_id: str
    campaign_title: str
    donor_user_id: str

    amount: Decimal
    currency: str = "BDT"
    payment_method: str = "bkash"

    status: DonationPaymentStatus
    merchant_invoice_number: str

    bkash_payment_id: str | None = None
    bkash_transaction_id: str | None = None
    provider_status: str | None = None
    failure_reason: str | None = None

    created_at: datetime
    updated_at: datetime
    paid_at: datetime | None = None