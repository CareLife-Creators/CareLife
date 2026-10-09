from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel


class OrganizationStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    VERIFIED = "verified"
    REJECTED = "rejected"
    NEEDS_CORRECTION = "needs_correction"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class Organization(BaseModel):
    organization_id: str
    organization_name: str
    organization_type: str
    description: str | None = None
    location: str | None = None
    contact: str | None = None

    license_number: str
    license_expiry_date: date

    submitted_by: str

    status: OrganizationStatus

    submitted_at: datetime
    updated_at: datetime

    message: str | None = None


class DaycareDirectoryEntry(BaseModel):
    organization_id: str
    organization_name: str
    organization_type: str
    description: str | None = None
    location: str | None = None
    contact: str | None = None
