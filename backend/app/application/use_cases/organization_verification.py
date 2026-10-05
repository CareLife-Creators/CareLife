from app.application.interfaces.organization import (
    OrganizationRepository,
)
from app.domain.entities.organization import (
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