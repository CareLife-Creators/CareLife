from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.interfaces.payment_gateway import (
    PaymentGatewayError,
)
from app.application.schemas.donation_payment import (
    BkashCallbackResponse,
    DonationPaymentCheckoutResponse,
    DonationPaymentCreateRequest,
    DonationPaymentResponse,
)
from app.application.use_cases.donation_payments import (
    DonationPaymentService,
)
from app.domain.entities.user_context import UserContext
from app.presentation.api.dependencies.authorization import get_current_user
from app.presentation.api.dependencies.donation_payment import (
    get_donation_payment_service,
)


router = APIRouter(tags=["bKash Donation Payments"])


def _raise_http_error(exc: Exception) -> None:
    if isinstance(exc, PermissionError):
        code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, LookupError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ValueError):
        code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, PaymentGatewayError):
        code = status.HTTP_502_BAD_GATEWAY
    else:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR

    raise HTTPException(
        status_code=code,
        detail=str(exc),
    ) from exc


@router.post(
    "/donation-campaigns/{campaign_id}/bkash-payments",
    response_model=DonationPaymentCheckoutResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_bkash_payment(
    campaign_id: str,
    request: DonationPaymentCreateRequest,
    current_user: UserContext = Depends(get_current_user),
    service: DonationPaymentService = Depends(
        get_donation_payment_service
    ),
):
    try:
        payment, payment_url = service.start_bkash_payment(
            current_user,
            campaign_id,
            request,
        )

        return DonationPaymentCheckoutResponse(
            payment=DonationPaymentResponse.from_entity(payment),
            payment_url=payment_url,
        )
    except (
        PermissionError,
        LookupError,
        ValueError,
        PaymentGatewayError,
    ) as exc:
        _raise_http_error(exc)


@router.get(
    "/donations/bkash/callback",
    response_model=BkashCallbackResponse,
)
def bkash_callback(
    paymentID: str = Query(min_length=1),
    status_value: str = Query(default="", alias="status"),
    service: DonationPaymentService = Depends(
        get_donation_payment_service
    ),
):
    try:
        payment = service.process_callback(
            bkash_payment_id=paymentID,
            callback_status=status_value,
        )

        messages = {
            "paid": "Payment verified successfully.",
            "failed": "Payment was not successful.",
            "cancelled": "Payment was cancelled.",
            "pending": "Payment is awaiting gateway confirmation.",
        }

        return BkashCallbackResponse(
            status=payment.status,
            receipt_number=payment.merchant_invoice_number,
            message=messages[payment.status.value],
        )
    except (
        PermissionError,
        LookupError,
        ValueError,
        PaymentGatewayError,
    ) as exc:
        _raise_http_error(exc)


@router.post(
    "/donations/payments/{payment_id}/verify",
    response_model=DonationPaymentResponse,
)
def verify_my_payment(
    payment_id: str,
    current_user: UserContext = Depends(get_current_user),
    service: DonationPaymentService = Depends(
        get_donation_payment_service
    ),
):
    try:
        payment = service.verify_payment(
            current_user,
            payment_id,
        )
        return DonationPaymentResponse.from_entity(payment)
    except (
        PermissionError,
        LookupError,
        ValueError,
        PaymentGatewayError,
    ) as exc:
        _raise_http_error(exc)


# Keep this route before /donations/payments/{payment_id}.
@router.get(
    "/donations/payments/me",
    response_model=list[DonationPaymentResponse],
)
def list_my_payments(
    current_user: UserContext = Depends(get_current_user),
    service: DonationPaymentService = Depends(
        get_donation_payment_service
    ),
):
    try:
        payments = service.list_my_payments(current_user)

        return [
            DonationPaymentResponse.from_entity(payment)
            for payment in payments
        ]
    except (
        PermissionError,
        LookupError,
        ValueError,
    ) as exc:
        _raise_http_error(exc)


@router.get(
    "/donations/payments/{payment_id}",
    response_model=DonationPaymentResponse,
)
def get_my_payment(
    payment_id: str,
    current_user: UserContext = Depends(
        get_current_user
    ),
    service: DonationPaymentService = Depends(
        get_donation_payment_service
    ),
):
    try:
        payment = service.get_my_payment(
            current_user,
            payment_id,
        )
        return DonationPaymentResponse.from_entity(payment)
    except (
        PermissionError,
        LookupError,
        ValueError,
    ) as exc:
        _raise_http_error(exc)
