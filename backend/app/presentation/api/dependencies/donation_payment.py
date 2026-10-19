from app.application.use_cases.donation_payments import (
    DonationPaymentService,
)
from app.core.config import get_settings
from app.infrastructure.gateways.bkash import BkashGatewayClient
from app.infrastructure.repositories.donation_payment import (
    PostgresDonationPaymentRepository,
)


def get_donation_payment_service() -> DonationPaymentService:
    settings = get_settings()

    return DonationPaymentService(
        repository=PostgresDonationPaymentRepository(),
        gateway=BkashGatewayClient(settings),
        callback_url=settings.bkash_callback_url,
    )