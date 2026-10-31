from functools import lru_cache

from app.application.use_cases.donation_payments import (
    DonationPaymentService,
)
from app.core.config import get_settings
from app.infrastructure.gateways.bkash import BkashGatewayClient
from app.infrastructure.repositories.donation_payment import (
    PostgresDonationPaymentRepository,
)


@lru_cache(maxsize=1)
def _get_bkash_gateway() -> BkashGatewayClient:
    return BkashGatewayClient(get_settings())


def get_donation_payment_service() -> DonationPaymentService:
    settings = get_settings()

    return DonationPaymentService(
        repository=PostgresDonationPaymentRepository(),
        gateway=_get_bkash_gateway(),
        callback_url=settings.bkash_callback_url,
    )
