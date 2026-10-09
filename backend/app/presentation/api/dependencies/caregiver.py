
from app.application.use_cases.caregivers import CaregiverService
from app.infrastructure.repositories.caregiver import (
    PostgresCaregiverRepository,
)


def get_caregiver_service() -> CaregiverService:
    return CaregiverService(
        repository=PostgresCaregiverRepository()
    )