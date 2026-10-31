import unittest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock

from app.application.interfaces.payment_gateway import PaymentGatewayError
from app.application.schemas.donation_payment import (
    DonationPaymentCreateRequest,
)
from app.application.use_cases.donation_payments import (
    DonationPaymentService,
)
from app.domain.entities.donation_payment import (
    DonationPayment,
    DonationPaymentStatus,
)
from app.domain.entities.user_context import Role, UserContext


class DonationPaymentServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = Mock()
        self.gateway = Mock()
        self.service = DonationPaymentService(
            repository=self.repository,
            gateway=self.gateway,
            callback_url="https://example.test/donations/bkash/callback",
        )
        self.donor = UserContext(
            user_id="donor-1",
            role=Role.DONOR_SUPPORTER,
        )
        self.parent = UserContext(
            user_id="parent-1",
            role=Role.PARENT_GUARDIAN,
        )
        now = datetime.now(timezone.utc)
        self.payment = DonationPayment(
            id="payment-1",
            campaign_id="campaign-1",
            campaign_title="Emergency Supplies",
            donor_user_id="donor-1",
            amount=Decimal("100.00"),
            currency="BDT",
            payment_method="bkash",
            status=DonationPaymentStatus.PENDING,
            merchant_invoice_number="CLTEST123",
            bkash_payment_id="bkash-payment-1",
            created_at=now,
            updated_at=now,
        )

    def test_donor_can_start_checkout(self):
        self.repository.create_pending_payment.return_value = self.payment
        self.repository.attach_gateway_payment.return_value = self.payment
        self.gateway.create_payment.return_value = {
            "paymentID": "bkash-payment-1",
            "bkashURL": "https://checkout.example.test/pay",
            "statusCode": "0000",
            "transactionStatus": "Initiated",
        }

        payment, payment_url = self.service.start_bkash_payment(
            self.donor,
            "campaign-1",
            DonationPaymentCreateRequest(amount=Decimal("100.00")),
        )

        self.assertEqual(payment.status, DonationPaymentStatus.PENDING)
        self.assertEqual(payment_url, "https://checkout.example.test/pay")
        self.repository.create_pending_payment.assert_called_once()
        self.repository.attach_gateway_payment.assert_called_once()

    def test_other_authenticated_role_can_start_checkout(self):
        parent_payment = self.payment.model_copy(
            update={"donor_user_id": self.parent.user_id}
        )
        self.repository.create_pending_payment.return_value = parent_payment
        self.repository.attach_gateway_payment.return_value = parent_payment
        self.gateway.create_payment.return_value = {
            "paymentID": "bkash-payment-1",
            "bkashURL": "https://checkout.example.test/pay",
            "statusCode": "0000",
            "transactionStatus": "Initiated",
        }

        payment, payment_url = self.service.start_bkash_payment(
            self.parent,
            "campaign-1",
            DonationPaymentCreateRequest(amount=Decimal("100.00")),
        )

        self.assertEqual(payment.donor_user_id, self.parent.user_id)
        self.assertEqual(payment_url, "https://checkout.example.test/pay")
        self.repository.create_pending_payment.assert_called_once()
        self.repository.attach_gateway_payment.assert_called_once()

    def test_tokenized_v2_checkout_response_is_saved(self):
        self.repository.create_pending_payment.return_value = self.payment
        self.repository.attach_gateway_payment.return_value = self.payment
        self.gateway.create_payment.return_value = {
            "paymentId": "bkash-payment-1",
            "bkashURL": "https://checkout.example.test/pay",
            "transactionStatus": "Initiated",
        }

        payment, payment_url = self.service.start_bkash_payment(
            self.donor,
            "campaign-1",
            DonationPaymentCreateRequest(amount=Decimal("100.00")),
        )

        self.assertEqual(payment.status, DonationPaymentStatus.PENDING)
        self.assertEqual(payment_url, "https://checkout.example.test/pay")
        self.repository.attach_gateway_payment.assert_called_once_with(
            payment_id="payment-1",
            bkash_payment_id="bkash-payment-1",
            provider_status="Initiated",
        )

    def test_checkout_gateway_failure_records_non_paid_state(self):
        self.repository.create_pending_payment.return_value = self.payment
        self.gateway.create_payment.side_effect = PaymentGatewayError(
            "Gateway unavailable"
        )

        with self.assertRaises(PaymentGatewayError):
            self.service.start_bkash_payment(
                self.donor,
                "campaign-1",
                DonationPaymentCreateRequest(amount=Decimal("100.00")),
            )

        self.repository.update_payment_result.assert_called_once_with(
            payment_id="payment-1",
            status=DonationPaymentStatus.FAILED,
            bkash_transaction_id=None,
            provider_status="CREATE_FAILED",
            failure_reason="The bKash checkout could not be initialized.",
        )

    def test_completed_gateway_response_marks_payment_paid(self):
        self.repository.get_payment_by_bkash_id.return_value = self.payment
        self.gateway.execute_payment.return_value = {
            "paymentID": "bkash-payment-1",
            "merchantInvoiceNumber": "CLTEST123",
            "amount": "100.00",
            "currency": "BDT",
            "transactionStatus": "Completed",
            "trxID": "BKASH-TRX-1",
        }
        paid = self.payment.model_copy(
            update={
                "status": DonationPaymentStatus.PAID,
                "bkash_transaction_id": "BKASH-TRX-1",
            }
        )
        self.repository.update_payment_result.return_value = paid

        result = self.service.process_callback(
            "bkash-payment-1",
            "success",
        )

        self.assertEqual(result.status, DonationPaymentStatus.PAID)
        self.repository.update_payment_result.assert_called_once_with(
            payment_id="payment-1",
            status=DonationPaymentStatus.PAID,
            bkash_transaction_id="BKASH-TRX-1",
            provider_status="Completed",
            failure_reason=None,
        )

    def test_tokenized_v2_response_fields_mark_payment_paid(self):
        self.repository.get_payment_by_bkash_id.return_value = self.payment
        self.gateway.execute_payment.return_value = {
            "paymentId": "bkash-payment-1",
            "merchantInvoiceNumber": "CLTEST123",
            "amount": "100.00",
            "currency": "BDT",
            "transactionStatus": "Completed",
            "trxId": "BKASH-TRX-V2",
        }
        paid = self.payment.model_copy(
            update={
                "status": DonationPaymentStatus.PAID,
                "bkash_transaction_id": "BKASH-TRX-V2",
            }
        )
        self.repository.update_payment_result.return_value = paid

        result = self.service.process_callback(
            "bkash-payment-1",
            "success",
        )

        self.assertEqual(result.status, DonationPaymentStatus.PAID)
        self.repository.update_payment_result.assert_called_once_with(
            payment_id="payment-1",
            status=DonationPaymentStatus.PAID,
            bkash_transaction_id="BKASH-TRX-V2",
            provider_status="Completed",
            failure_reason=None,
        )

    def test_tokenized_v2_query_response_can_verify_payment(self):
        self.repository.get_payment_by_bkash_id.return_value = self.payment
        self.gateway.execute_payment.side_effect = PaymentGatewayError(
            "Execute response was interrupted"
        )
        self.gateway.query_payment.return_value = {
            "paymentId": "bkash-payment-1",
            "merchantInvoice": "CLTEST123",
            "amount": "100.00",
            "currency": "BDT",
            "transactionStatus": "Completed",
            "trxId": "BKASH-QUERY-TRX",
        }
        paid = self.payment.model_copy(
            update={
                "status": DonationPaymentStatus.PAID,
                "bkash_transaction_id": "BKASH-QUERY-TRX",
            }
        )
        self.repository.update_payment_result.return_value = paid

        result = self.service.process_callback(
            "bkash-payment-1",
            "success",
        )

        self.assertEqual(result.status, DonationPaymentStatus.PAID)
        self.gateway.query_payment.assert_called_once_with(
            "bkash-payment-1"
        )
        self.repository.update_payment_result.assert_called_once_with(
            payment_id="payment-1",
            status=DonationPaymentStatus.PAID,
            bkash_transaction_id="BKASH-QUERY-TRX",
            provider_status="Completed",
            failure_reason=None,
        )

    def test_mismatched_amount_never_marks_payment_paid(self):
        self.repository.get_payment_by_bkash_id.return_value = self.payment
        self.gateway.execute_payment.return_value = {
            "paymentID": "bkash-payment-1",
            "merchantInvoiceNumber": "CLTEST123",
            "amount": "999.00",
            "currency": "BDT",
            "transactionStatus": "Completed",
            "trxID": "BKASH-TRX-2",
        }
        failed = self.payment.model_copy(
            update={
                "status": DonationPaymentStatus.FAILED,
                "failure_reason": (
                    "The gateway response did not match the payment."
                ),
            }
        )
        self.repository.update_payment_result.return_value = failed

        result = self.service.process_callback(
            "bkash-payment-1",
            "success",
        )

        self.assertNotEqual(result.status, DonationPaymentStatus.PAID)
        self.repository.update_payment_result.assert_called_once_with(
            payment_id="payment-1",
            status=DonationPaymentStatus.FAILED,
            bkash_transaction_id=None,
            provider_status="INCONSISTENT_RESPONSE",
            failure_reason="The gateway response did not match the payment.",
        )

    def test_gateway_failure_status_keeps_payment_non_paid(self):
        self.repository.get_payment_by_bkash_id.return_value = self.payment
        self.gateway.query_payment.return_value = {
            "paymentID": "bkash-payment-1",
            "transactionStatus": "Failed",
        }
        failed = self.payment.model_copy(
            update={"status": DonationPaymentStatus.FAILED}
        )
        self.repository.update_payment_result.return_value = failed

        result = self.service.process_callback(
            "bkash-payment-1",
            "failure",
        )

        self.assertEqual(result.status, DonationPaymentStatus.FAILED)
        self.gateway.query_payment.assert_called_once_with(
            "bkash-payment-1"
        )

    def test_donor_cannot_verify_another_donors_payment(self):
        self.repository.get_payment_for_donor.return_value = None

        with self.assertRaises(LookupError):
            self.service.verify_payment(self.donor, "payment-not-owned")

        self.repository.get_payment_for_donor.assert_called_once_with(
            "payment-not-owned",
            "donor-1",
        )
        self.gateway.query_payment.assert_not_called()

    def test_callback_failure_hint_cannot_override_gateway_pending_status(self):
        self.repository.get_payment_by_bkash_id.return_value = self.payment
        self.gateway.query_payment.return_value = {
            "paymentID": "bkash-payment-1",
            "transactionStatus": "Initiated",
        }
        self.repository.update_payment_result.return_value = self.payment

        result = self.service.process_callback(
            "bkash-payment-1",
            "failure",
        )

        self.assertEqual(result.status, DonationPaymentStatus.PENDING)
        self.gateway.query_payment.assert_called_once_with(
            "bkash-payment-1"
        )
        self.repository.update_payment_result.assert_called_once_with(
            payment_id="payment-1",
            status=DonationPaymentStatus.PENDING,
            bkash_transaction_id=None,
            provider_status="Initiated",
            failure_reason=None,
        )

    def test_unknown_callback_payment_is_rejected(self):
        self.repository.get_payment_by_bkash_id.return_value = None

        with self.assertRaises(LookupError):
            self.service.process_callback("unknown-payment", "success")

        self.gateway.execute_payment.assert_not_called()
        self.gateway.query_payment.assert_not_called()


if __name__ == "__main__":
    unittest.main()
