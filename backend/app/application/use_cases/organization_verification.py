from app.application.interfaces.organization_verification import (
    OrganizationVerificationRepository,
)
from app.domain.entities.organization_verification import (
    VerificationStatus,
)


class OrganizationVerificationService:
    def __init__(
        self,
        repository: OrganizationVerificationRepository,
    ):
        self.repository = repository

    def get_status(self, organization_id: str):
        verification = self.repository.get_by_organization_id(
            organization_id
        )

        if verification is None:
            raise ValueError(
                "Verification information not found"
            )

        return verification

    def get_pending(self):
        return self.repository.get_pending()

    def approve(self, organization_id: str):
        verification = self.repository.get_by_organization_id(
            organization_id
        )

        if verification is None:
            raise ValueError(
                "Verification information not found"
            )

        if verification.status != VerificationStatus.PENDING:
            raise ValueError(
                "Only pending organizations can be approved"
            )

        updated = self.repository.approve(organization_id)

        if updated is None:
            raise ValueError(
                "Verification information not found"
            )

        return updated

    def reject(
        self,
        organization_id: str,
        message: str | None = None,
    ):
        verification = self.repository.get_by_organization_id(
            organization_id
        )

        if verification is None:
            raise ValueError(
                "Verification information not found"
            )

        if verification.status != VerificationStatus.PENDING:
            raise ValueError(
                "Only pending organizations can be rejected"
            )

        updated = self.repository.reject(
            organization_id,
            message,
        )

        if updated is None:
            raise ValueError(
                "Verification information not found"
            )

        return updated