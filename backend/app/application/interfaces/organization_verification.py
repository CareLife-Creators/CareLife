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

    def get_pending(self) -> list[OrganizationVerification]:
        ...

    def approve(
        self,
        organization_id: str,
    ) -> OrganizationVerification | None:
        ...

    def reject(
        self,
        organization_id: str,
        message: str | None = None,
    ) -> OrganizationVerification | None:
        ...