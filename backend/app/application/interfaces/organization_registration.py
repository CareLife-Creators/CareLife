from typing import Protocol

from app.domain.entities.organization_registration import (
    OrganizationRegistration,
)


class OrganizationRegistrationRepository(Protocol):
    def create(
        self,
        registration: OrganizationRegistration,
    ) -> OrganizationRegistration:
        ...
