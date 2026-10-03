from app.application.use_cases.organization_registration import (
    OrganizationRegistrationService,
)
from app.infrastructure.repositories.organization_registration_repository import (
    PostgresOrganizationRegistrationRepository,
)


def get_organization_registration_service() -> (
    OrganizationRegistrationService
):
    repository = PostgresOrganizationRegistrationRepository()

    return OrganizationRegistrationService(
        repository=repository
    )
