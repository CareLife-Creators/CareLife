from datetime import datetime, timezone
from uuid import uuid4

from app.application.interfaces.organization_registration import (
    OrganizationRegistrationRepository,
)
from app.application.schemas.organization_registration import (
    OrganizationRegistrationRequest,
)
from app.domain.entities.organization_registration import (
    OrganizationRegistration,
    RegistrationStatus,
)


class OrganizationRegistrationService:
    def __init__(
        self,
        repository: OrganizationRegistrationRepository,
    ):
        self.repository = repository

    def register(
        self,
        request: OrganizationRegistrationRequest,
        submitted_by: str,
    ) -> OrganizationRegistration:
        registration = OrganizationRegistration(
            organization_id=str(uuid4()),
            organization_name=request.organization_name,
            organization_type=request.organization_type,
            license_number=request.license_number,
            license_expiry_date=request.license_expiry_date,
            submitted_by=submitted_by,
            status=RegistrationStatus.PENDING,
            submitted_at=datetime.now(timezone.utc),
        )

        return self.repository.create(registration)
