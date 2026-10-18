from app.application.use_cases.in_kind_donations import (
    InKindDonationService,
)
from app.infrastructure.repositories.in_kind_donation import (
    PostgresInKindDonationRepository,
)


def get_in_kind_donation_service() -> InKindDonationService:
    return InKindDonationService(
        PostgresInKindDonationRepository()
    )