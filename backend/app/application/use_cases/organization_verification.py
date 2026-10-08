from app.application.interfaces.organization import (
    OrganizationRepository,
)
from app.domain.entities.organization import (
    DaycareDirectoryEntry,
    OrganizationStatus,
)


class OrganizationVerificationService:

    def __init__(
        self,
        repository: OrganizationRepository,
    ):
        self.repository = repository

    def get_status(
        self,
        organization_id: str,
    ):

        organization = (
            self.repository.get_by_organization_id(
                organization_id
            )
        )

        if organization is None:
            raise ValueError(
                "Verification information not found"
            )

        return organization

    def get_pending(self):

        return self.repository.get_pending()

    def approve(
        self,
        organization_id: str,
        reviewer_id: str,
    ):

        organization = (
            self.repository.get_by_organization_id(
                organization_id
            )
        )

        if organization is None:
            raise ValueError(
                "Verification information not found"
            )

        if organization.status != OrganizationStatus.PENDING:
            raise ValueError(
                "Only pending organizations can be approved"
            )

        updated = self.repository.approve(
            organization_id,
            reviewer_id,
        )

        if updated is None:
            raise ValueError(
                "Verification information not found"
            )

        return updated

    def reject(
        self,
        organization_id: str,
        reviewer_id: str,
        message: str | None = None,
    ):

        organization = (
            self.repository.get_by_organization_id(
                organization_id
            )
        )

        if organization is None:
            raise ValueError(
                "Verification information not found"
            )

        if organization.status != OrganizationStatus.PENDING:
            raise ValueError(
                "Only pending organizations can be rejected"
            )

        updated = self.repository.reject(
            organization_id,
            reviewer_id,
            message,
        )

        if updated is None:
            raise ValueError(
                "Verification information not found"
            )

        return updated

    def get_daycare_directory(
        self,
        search: str | None = None,
        location: str | None = None,
    ) -> list[DaycareDirectoryEntry]:

        clean_search = (
            search.strip()
            if isinstance(search, str)
            else None
        )

        clean_location = (
            location.strip()
            if isinstance(location, str)
            else None
        )

        if clean_search == "":
            clean_search = None

        if clean_location == "":
            clean_location = None

        return self.repository.get_daycare_directory(
            search=clean_search,
            location=clean_location,
        )

    def get_public_daycare(
        self,
        organization_id: str,
    ) -> DaycareDirectoryEntry:

        daycare = self.repository.get_public_daycare(
            organization_id
        )

        if daycare is None:
            raise ValueError(
                "Verified daycare not found"
            )

        return daycare