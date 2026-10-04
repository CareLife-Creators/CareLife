from typing import Protocol

from app.domain.entities.organization import Organization


class OrganizationRepository(Protocol):

    def create(
        self,
        organization: Organization,
    ) -> Organization:
        ...

    def get_by_organization_id(
        self,
        organization_id: str,
    ) -> Organization | None:
        ...

    def get_pending(
        self,
    ) -> list[Organization]:
        ...

    def approve(
        self,
        organization_id: str,
        reviewer_id: str,
    ) -> Organization | None:
        ...

    def reject(
        self,
        organization_id: str,
        reviewer_id: str,
        message: str | None = None,
    ) -> Organization | None:
        ...