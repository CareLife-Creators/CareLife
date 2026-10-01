from app.application.interfaces.organization_verification import (
    OrganizationVerificationRepository,
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