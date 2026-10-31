from decimal import Decimal
from typing import Any, Protocol


class PaymentGatewayError(RuntimeError):
    """A payment gateway request could not be completed safely."""


class BkashPaymentGateway(Protocol):
    def validate_configuration(self) -> None:
        ...

    def create_payment(
        self,
        amount: Decimal,
        currency: str,
        merchant_invoice_number: str,
        callback_url: str,
        payer_reference: str,
    ) -> dict[str, Any]:
        ...

    def execute_payment(
        self,
        bkash_payment_id: str,
    ) -> dict[str, Any]:
        ...

    def query_payment(
        self,
        bkash_payment_id: str,
    ) -> dict[str, Any]:
        ...
