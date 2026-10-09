from typing import Protocol

from app.domain.entities.organization import (
    DaycareDirectoryEntry,
    Organization,
)


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

    def get_daycare_directory(
        self,
        search: str | None = None,
        location: str | None = None,
    ) -> list[DaycareDirectoryEntry]:
        ...

    def get_public_daycare(
        self,
        organization_id: str,
    ) -> DaycareDirectoryEntry | None:
        ...

    def expire_verified_organizations(self) -> int:
        ...

    def create_license_expiry_reminders(
        self,
        reminder_days: int,
    ) -> int:
        ...