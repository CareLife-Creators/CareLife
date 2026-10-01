from app.application.use_cases.organization_verification import (
    OrganizationVerificationService,
)
from app.infrastructure.repositories.organization_verification_repository import (
    PostgresOrganizationVerificationRepository,
)


def get_organization_verification_service() -> (
    OrganizationVerificationService
):
    repository = PostgresOrganizationVerificationRepository()

    return OrganizationVerificationService(
        repository=repository
    )