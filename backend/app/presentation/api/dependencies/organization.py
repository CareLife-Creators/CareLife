from app.application.use_cases.organization_registration import (
    OrganizationRegistrationService,
)
from app.application.use_cases.organization_verification import (
    OrganizationVerificationService,
)
from app.infrastructure.repositories.organization_repository import (
    PostgresOrganizationRepository,
)


def get_organization_repository() -> (
    PostgresOrganizationRepository
):
    return PostgresOrganizationRepository()


def get_organization_registration_service(
) -> OrganizationRegistrationService:

    repository = get_organization_repository()

    return OrganizationRegistrationService(
        repository=repository
    )


def get_organization_verification_service(
) -> OrganizationVerificationService:

    repository = get_organization_repository()

    return OrganizationVerificationService(
        repository=repository
    )