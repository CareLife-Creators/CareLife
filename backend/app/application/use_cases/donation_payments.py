from decimal import Decimal, InvalidOperation
from uuid import uuid4

from app.application.interfaces.donation_payment import (
    DonationPaymentRepository,
)
from app.application.interfaces.payment_gateway import (
    BkashPaymentGateway,
    PaymentGatewayError,
)
from app.application.schemas.donation_payment import (
    DonationPaymentCreateRequest,
)
from app.domain.entities.donation_payment import (
    DonationPayment,
    DonationPaymentStatus,
)
from app.domain.entities.user_context import Role, UserContext


class DonationPaymentService:
    def __init__(
        self,
        repository: DonationPaymentRepository,
        gateway: BkashPaymentGateway,
        callback_url: str,
    ):
        self.repository = repository
        self.gateway = gateway
        self.callback_url = callback_url

    @staticmethod
    def _require_donor(user: UserContext) -> None:
        if user.role != Role.DONOR_SUPPORTER:
            raise PermissionError(
                "Donor-supporter access is required."
            )

    def start_bkash_payment(
        self,
        user: UserContext,
        campaign_id: str,
        request: DonationPaymentCreateRequest,
    ) -> tuple[DonationPayment, str]:
        self._require_donor(user)

        invoice_number = f"CL{uuid4().hex[:24].upper()}"

        payment = self.repository.create_pending_payment(
            campaign_id=campaign_id,
            donor_user_id=user.user_id,
            amount=request.amount,
            merchant_invoice_number=invoice_number,
        )

        try:
            result = self.gateway.create_payment(
                amount=payment.amount,
                currency=payment.currency,
                merchant_invoice_number=payment.merchant_invoice_number,
                callback_url=self.callback_url,
                payer_reference=payment.merchant_invoice_number,
            )

            bkash_payment_id = result.get("paymentID")
            payment_url = result.get("bkashURL")

            if (
                not isinstance(bkash_payment_id, str)
                or not bkash_payment_id.strip()
                or not isinstance(payment_url, str)
                or not payment_url.startswith("https://")
            ):
                raise PaymentGatewayError(
                    "The bKash gateway returned an invalid checkout response."
                )

            saved_payment = self.repository.attach_gateway_payment(
                payment_id=payment.id,
                bkash_payment_id=bkash_payment_id,
                provider_status=(
                    str(result.get("transactionStatus") or "Initiated")[:100]
                ),
            )

            return saved_payment, payment_url

        except PaymentGatewayError:
            self.repository.update_payment_result(
                payment_id=payment.id,
                status=DonationPaymentStatus.FAILED,
                bkash_transaction_id=None,
                provider_status="CREATE_FAILED",
                failure_reason=(
                    "The bKash checkout could not be initialized."
                ),
            )
            raise

    def _apply_gateway_result(
        self,
        payment: DonationPayment,
        result: dict,
    ) -> DonationPayment:
        provider_status = str(
            result.get("transactionStatus") or "Unknown"
        )[:100]

        normalized_status = provider_status.casefold()

        if normalized_status == "completed":
            try:
                returned_amount = Decimal(str(result.get("amount")))
            except (InvalidOperation, TypeError, ValueError):
                returned_amount = None

            matches_payment = (
                str(result.get("paymentID") or "")
                == str(payment.bkash_payment_id or "")
            )
            matches_invoice = (
                str(result.get("merchantInvoiceNumber") or "")
                == payment.merchant_invoice_number
            )
            matches_amount = returned_amount == payment.amount
            matches_currency = (
                str(result.get("currency") or "").upper()
                == payment.currency
            )
            transaction_id = str(result.get("trxID") or "").strip()

            # Only the gateway's server response can finalize a payment.
            if not all(
                (
                    matches_payment,
                    matches_invoice,
                    matches_amount,
                    matches_currency,
                    bool(transaction_id),
                )
            ):
                return self._save_result(
                    payment.id,
                    DonationPaymentStatus.FAILED,
                    None,
                    "INCONSISTENT_RESPONSE",
                    "The gateway response did not match the payment.",
                )

            return self._save_result(
                payment.id,
                DonationPaymentStatus.PAID,
                transaction_id,
                provider_status,
                None,
            )

        if normalized_status in {
            "cancelled",
            "canceled",
            "voided",
        }:
            return self._save_result(
                payment.id,
                DonationPaymentStatus.CANCELLED,
                None,
                provider_status,
                "The bKash payment was cancelled.",
            )

        if normalized_status in {
            "failed",
            "failure",
            "rejected",
            "declined",
            "error",
        }:
            return self._save_result(
                payment.id,
                DonationPaymentStatus.FAILED,
                None,
                provider_status,
                "The bKash payment was not successful.",
            )

        return self._save_result(
            payment.id,
            DonationPaymentStatus.PENDING,
            None,
            provider_status,
            None,
        )

    def _save_result(
        self,
        payment_id: str,
        status: DonationPaymentStatus,
        bkash_transaction_id: str | None,
        provider_status: str | None,
        failure_reason: str | None,
    ) -> DonationPayment:
        payment = self.repository.update_payment_result(
            payment_id=payment_id,
            status=status,
            bkash_transaction_id=bkash_transaction_id,
            provider_status=provider_status,
            failure_reason=failure_reason,
        )

        if payment is None:
            raise LookupError("Payment transaction not found.")

        return payment

    def process_callback(
        self,
        bkash_payment_id: str,
        callback_status: str,
    ) -> DonationPayment:
        payment = self.repository.get_payment_by_bkash_id(
            bkash_payment_id
        )

        if payment is None:
            raise LookupError(
                "No matching bKash payment transaction was found."
            )

        if payment.status == DonationPaymentStatus.PAID:
            return payment

        if callback_status.strip().casefold() == "success":
            try:
                result = self.gateway.execute_payment(
                    bkash_payment_id
                )
            except PaymentGatewayError:
                # Execution may have completed even if its response
                # was interrupted. Query the gateway before deciding.
                result = self.gateway.query_payment(
                    bkash_payment_id
                )
        else:
            result = self.gateway.query_payment(
                bkash_payment_id
            )

        return self._apply_gateway_result(
            payment,
            result,
        )

    def verify_payment(
        self,
        user: UserContext,
        payment_id: str,
    ) -> DonationPayment:
        self._require_donor(user)

        payment = self.repository.get_payment_for_donor(
            payment_id,
            user.user_id,
        )

        if payment is None:
            raise LookupError("Payment transaction not found.")

        if payment.status == DonationPaymentStatus.PAID:
            return payment

        if not payment.bkash_payment_id:
            raise ValueError(
                "The bKash payment has not been initialized."
            )

        result = self.gateway.query_payment(
            payment.bkash_payment_id
        )

        return self._apply_gateway_result(payment, result)

    def list_my_payments(
        self,
        user: UserContext,
    ) -> list[DonationPayment]:
        self._require_donor(user)

        return self.repository.list_payments_for_donor(
            user.user_id
        )

    def get_my_payment(
        self,
        user: UserContext,
        payment_id: str,
    ) -> DonationPayment:
        self._require_donor(user)

        payment = self.repository.get_payment_for_donor(
            payment_id,
            user.user_id,
        )

        if payment is None:
            raise LookupError("Payment transaction not found.")

        return payment