from datetime import datetime, timezone
from uuid import uuid4

from app.application.interfaces.organization import (
    OrganizationRepository,
)
from app.application.schemas.organization import (
    OrganizationRegistrationRequest,
)
from app.domain.entities.organization import (
    Organization,
    OrganizationStatus,
)


class OrganizationRegistrationService:

    def __init__(
        self,
        repository: OrganizationRepository,
    ):
        self.repository = repository

    def register(
        self,
        request: OrganizationRegistrationRequest,
        submitted_by: str,
    ) -> Organization:

        now = datetime.now(timezone.utc)

        organization = Organization(
            organization_id=str(uuid4()),
            organization_name=request.organization_name,
            organization_type=request.organization_type,
            license_number=request.license_number,
            license_expiry_date=request.license_expiry_date,
            submitted_by=submitted_by,
            status=OrganizationStatus.PENDING,
            submitted_at=now,
            updated_at=now,
        )

        return self.repository.create(
            organization
        )