from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities.donation_payment import (
    DonationPayment,
    DonationPaymentStatus,
)


class DonationPaymentCreateRequest(BaseModel):
    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )


class DonationPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    campaign_id: str
    campaign_title: str
    donor_user_id: str

    amount: Decimal
    currency: str
    payment_method: str
    status: DonationPaymentStatus
    merchant_invoice_number: str

    bkash_payment_id: str | None = None
    bkash_transaction_id: str | None = None
    provider_status: str | None = None
    failure_reason: str | None = None

    created_at: datetime
    updated_at: datetime
    paid_at: datetime | None = None

    @classmethod
    def from_entity(
        cls,
        payment: DonationPayment,
    ) -> "DonationPaymentResponse":
        return cls(
            id=payment.id,
            campaign_id=payment.campaign_id,
            campaign_title=payment.campaign_title,
            donor_user_id=payment.donor_user_id,
            amount=payment.amount,
            currency=payment.currency,
            payment_method=payment.payment_method,
            status=payment.status,
            merchant_invoice_number=payment.merchant_invoice_number,
            bkash_payment_id=payment.bkash_payment_id,
            bkash_transaction_id=payment.bkash_transaction_id,
            provider_status=payment.provider_status,
            failure_reason=payment.failure_reason,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
            paid_at=payment.paid_at,
        )


class DonationPaymentCheckoutResponse(BaseModel):
    payment: DonationPaymentResponse
    payment_url: str


class BkashCallbackResponse(BaseModel):
    status: DonationPaymentStatus
    receipt_number: str
    message: str