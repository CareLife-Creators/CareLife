from app.application.use_cases.elder_care_booking import (
    ElderCareBookingService,
)
from app.infrastructure.repositories.elder_care_booking import (
    PostgresElderCareBookingRepository,
)


def get_elder_care_booking_service() -> ElderCareBookingService:
    return ElderCareBookingService(
        repository=PostgresElderCareBookingRepository(),
    )