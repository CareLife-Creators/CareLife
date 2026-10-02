from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class VerificationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class OrganizationVerification(BaseModel):
    organization_id: str
    organization_name: str
    organization_type: str
    status: VerificationStatus
    submitted_at: datetime
    updated_at: datetime
    message: str | None = None