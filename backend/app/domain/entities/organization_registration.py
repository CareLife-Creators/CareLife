from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel


class RegistrationStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    NEEDS_CORRECTION = "needs_correction"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class OrganizationRegistration(BaseModel):
    organization_id: str
    organization_name: str
    organization_type: str
    license_number: str
    license_expiry_date: date
    submitted_by: str
    status: RegistrationStatus = RegistrationStatus.PENDING
    submitted_at: datetime