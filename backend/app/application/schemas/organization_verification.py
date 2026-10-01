from datetime import datetime

from pydantic import BaseModel

from app.domain.entities.organization_verification import (
    VerificationStatus,
)


class OrganizationVerificationResponse(BaseModel):
    organization_id: str
    organization_name: str
    organization_type: str
    status: VerificationStatus
    submitted_at: datetime
    updated_at: datetime
    message: str | None = None