from app.application.use_cases.caregiver_booking import (
    CaregiverBookingService,
)
from app.infrastructure.repositories.caregiver_booking import (
    PostgresCaregiverBookingRepository,
)


def get_caregiver_booking_service() -> CaregiverBookingService:
    return CaregiverBookingService(
        repository=PostgresCaregiverBookingRepository()
    )