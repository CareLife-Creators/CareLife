from typing import Protocol

from app.domain.entities.organization_profile import (
    OrganizationProfile,
)


class OrganizationProfileRepository(Protocol):

    def get_for_staff(
        self,
        organization_id: str,
    ) -> OrganizationProfile | None:
        ...

    def get_public(
        self,
        organization_id: str,
    ) -> OrganizationProfile | None:
        ...

    def update_profile(
        self,
        organization_id: str,
        changes: dict[str, object],
        updated_by: str,
    ) -> OrganizationProfile | None:
        ...