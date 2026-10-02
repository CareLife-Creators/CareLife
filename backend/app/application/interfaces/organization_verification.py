from typing import Protocol

from app.domain.entities.organization_verification import (
    OrganizationVerification,
)


class OrganizationVerificationRepository(Protocol):
    def get_by_organization_id(
        self,
        organization_id: str,
    ) -> OrganizationVerification | None:
        ...