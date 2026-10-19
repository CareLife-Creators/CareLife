from decimal import Decimal
from typing import Protocol

from app.domain.entities.donation_payment import (
    DonationPayment,
    DonationPaymentStatus,
)


class DonationPaymentRepository(Protocol):
    def create_pending_payment(
        self,
        campaign_id: str,
        donor_user_id: str,
        amount: Decimal,
        merchant_invoice_number: str,
    ) -> DonationPayment:
        ...

    def attach_gateway_payment(
        self,
        payment_id: str,
        bkash_payment_id: str,
        provider_status: str | None,
    ) -> DonationPayment:
        ...

    def update_payment_result(
        self,
        payment_id: str,
        status: DonationPaymentStatus,
        bkash_transaction_id: str | None,
        provider_status: str | None,
        failure_reason: str | None,
    ) -> DonationPayment | None:
        ...

    def get_payment(
        self,
        payment_id: str,
    ) -> DonationPayment | None:
        ...

    def get_payment_by_bkash_id(
        self,
        bkash_payment_id: str,
    ) -> DonationPayment | None:
        ...

    def get_payment_for_donor(
        self,
        payment_id: str,
        donor_user_id: str,
    ) -> DonationPayment | None:
        ...

    def list_payments_for_donor(
        self,
        donor_user_id: str,
    ) -> list[DonationPayment]:
        ...