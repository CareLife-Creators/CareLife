from app.application.use_cases.donations import DonationService
from app.infrastructure.repositories.donation import PostgresDonationRepository


def get_donation_service() -> DonationService:
    return DonationService(PostgresDonationRepository())
