from decimal import Decimal
from uuid import uuid4

from app.application.interfaces.donation_payment import (
    DonationPaymentRepository,
)
from app.domain.entities.donation_payment import (
    DonationPayment,
    DonationPaymentStatus,
)
from app.infrastructure.database.connection import get_connection


_PAYMENT_SELECT = """
    SELECT
        p.id,
        p.campaign_id,
        c.title,
        p.donor_user_id,
        p.amount,
        p.currency,
        p.payment_method,
        p.status,
        p.merchant_invoice_number,
        p.bkash_payment_id,
        p.bkash_transaction_id,
        p.provider_status,
        p.failure_reason,
        p.created_at,
        p.updated_at,
        p.paid_at
    FROM donation_payments p
    JOIN donation_campaigns c ON c.id = p.campaign_id
"""


class PostgresDonationPaymentRepository(DonationPaymentRepository):
    @staticmethod
    def _from_row(row) -> DonationPayment | None:
        if row is None:
            return None

        return DonationPayment(
            id=row[0],
            campaign_id=row[1],
            campaign_title=row[2],
            donor_user_id=row[3],
            amount=Decimal(str(row[4])),
            currency=row[5],
            payment_method=row[6],
            status=DonationPaymentStatus(row[7]),
            merchant_invoice_number=row[8],
            bkash_payment_id=row[9],
            bkash_transaction_id=row[10],
            provider_status=row[11],
            failure_reason=row[12],
            created_at=row[13],
            updated_at=row[14],
            paid_at=row[15],
        )

    def create_pending_payment(
        self,
        campaign_id: str,
        donor_user_id: str,
        amount: Decimal,
        merchant_invoice_number: str,
    ) -> DonationPayment:
        with get_connection() as connection:
            with connection.transaction():
                campaign = connection.execute(
                    """
                    SELECT c.currency
                    FROM donation_campaigns c
                    JOIN organizations o
                      ON o.id = c.organization_id
                    JOIN verification_statuses vs
                      ON vs.id = o.status_id
                    WHERE c.id = %s
                      AND c.is_active = TRUE
                      AND vs.name = 'verified'
                    FOR SHARE OF c
                    """,
                    (campaign_id,),
                ).fetchone()

                if campaign is None:
                    raise LookupError(
                        "Active donation campaign not found."
                    )

                currency = str(campaign[0]).upper()
                if currency != "BDT":
                    raise ValueError(
                        "bKash payments are only supported for BDT campaigns."
                    )

                payment_id = str(uuid4())

                connection.execute(
                    """
                    INSERT INTO donation_payments (
                        id,
                        campaign_id,
                        donor_user_id,
                        amount,
                        currency,
                        payment_method,
                        status,
                        merchant_invoice_number,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        %s, %s, %s, %s, 'BDT', 'bkash', 'pending',
                        %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                    """,
                    (
                        payment_id,
                        campaign_id,
                        donor_user_id,
                        amount,
                        merchant_invoice_number,
                    ),
                )

                row = connection.execute(
                    _PAYMENT_SELECT + " WHERE p.id = %s",
                    (payment_id,),
                ).fetchone()

        payment = self._from_row(row)
        if payment is None:
            raise RuntimeError(
                "The payment transaction could not be reloaded."
            )
        return payment

    def attach_gateway_payment(
        self,
        payment_id: str,
        bkash_payment_id: str,
        provider_status: str | None,
    ) -> DonationPayment:
        with get_connection() as connection:
            with connection.transaction():
                result = connection.execute(
                    """
                    UPDATE donation_payments
                    SET
                        bkash_payment_id = %s,
                        provider_status = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                      AND status = 'pending'
                    """,
                    (
                        bkash_payment_id,
                        provider_status,
                        payment_id,
                    ),
                )

                if result.rowcount == 0:
                    raise LookupError(
                        "The pending payment transaction was not found."
                    )

                row = connection.execute(
                    _PAYMENT_SELECT + " WHERE p.id = %s",
                    (payment_id,),
                ).fetchone()

        payment = self._from_row(row)
        if payment is None:
            raise LookupError("Payment transaction not found.")
        return payment

    def update_payment_result(
        self,
        payment_id: str,
        status: DonationPaymentStatus,
        bkash_transaction_id: str | None,
        provider_status: str | None,
        failure_reason: str | None,
    ) -> DonationPayment | None:
        with get_connection() as connection:
            with connection.transaction():
                connection.execute(
                    """
                    UPDATE donation_payments
                    SET
                        status = %s,
                        bkash_transaction_id = COALESCE(
                            %s, bkash_transaction_id
                        ),
                        provider_status = %s,
                        failure_reason = %s,
                        paid_at = CASE
                            WHEN %s = 'paid'
                            THEN COALESCE(paid_at, CURRENT_TIMESTAMP)
                            ELSE paid_at
                        END,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                      AND status <> 'paid'
                    """,
                    (
                        status.value,
                        bkash_transaction_id,
                        provider_status,
                        failure_reason,
                        status.value,
                        payment_id,
                    ),
                )

                row = connection.execute(
                    _PAYMENT_SELECT + " WHERE p.id = %s",
                    (payment_id,),
                ).fetchone()

        return self._from_row(row)

    def get_payment(
        self,
        payment_id: str,
    ) -> DonationPayment | None:
        with get_connection() as connection:
            row = connection.execute(
                _PAYMENT_SELECT + " WHERE p.id = %s",
                (payment_id,),
            ).fetchone()

        return self._from_row(row)

    def get_payment_by_bkash_id(
        self,
        bkash_payment_id: str,
    ) -> DonationPayment | None:
        with get_connection() as connection:
            row = connection.execute(
                _PAYMENT_SELECT
                + " WHERE p.bkash_payment_id = %s",
                (bkash_payment_id,),
            ).fetchone()

        return self._from_row(row)

    def get_payment_for_donor(
        self,
        payment_id: str,
        donor_user_id: str,
    ) -> DonationPayment | None:
        with get_connection() as connection:
            row = connection.execute(
                _PAYMENT_SELECT
                + """
                    WHERE p.id = %s
                      AND p.donor_user_id = %s
                """,
                (payment_id, donor_user_id),
            ).fetchone()

        return self._from_row(row)

    def list_payments_for_donor(
        self,
        donor_user_id: str,
    ) -> list[DonationPayment]:
        with get_connection() as connection:
            rows = connection.execute(
                _PAYMENT_SELECT
                + """
                    WHERE p.donor_user_id = %s
                    ORDER BY p.created_at DESC, p.id DESC
                """,
                (donor_user_id,),
            ).fetchall()

        return [
            self._from_row(row)
            for row in rows
        ]