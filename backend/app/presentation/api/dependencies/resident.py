from app.application.use_cases.residents import (
    ResidentProfileService,
)
from app.infrastructure.repositories.residents import (
    PostgresResidentProfileRepository,
)


def get_resident_profile_service() -> ResidentProfileService:
    return ResidentProfileService(
        repository=PostgresResidentProfileRepository(),
    )