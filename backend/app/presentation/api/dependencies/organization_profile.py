from app.application.interfaces.organization_profile import (
    OrganizationProfileRepository,
)
from app.application.use_cases.organization_profile import (
    OrganizationProfileService,
)
from app.infrastructure.repositories.organization_profile_repository import (
    PostgresOrganizationProfileRepository,
)


def get_organization_profile_service(
) -> OrganizationProfileService:
    repository: OrganizationProfileRepository = (
        PostgresOrganizationProfileRepository()
    )

    return OrganizationProfileService(
        repository=repository,
    )