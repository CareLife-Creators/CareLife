from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


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
    latitude: float | None = None
    longitude: float | None = None
    contact: str | None = None
    capacity: int = 20
    age_range: str | None = None
    opening_hours: str | None = None
    facilities: str | None = None
    fees: str | None = None

    license_number: str
    license_expiry_date: date

    submitted_by: str

    status: OrganizationStatus

    submitted_at: datetime
    updated_at: datetime

    message: str | None = None


class OrganizationReviewEvent(BaseModel):
    status: OrganizationStatus
    reviewer_name: str | None = None
    notes: str | None = None
    reviewed_at: datetime


class OrganizationTrackingRecord(BaseModel):
    organization_id: str
    organization_name: str
    organization_type: str
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    status: OrganizationStatus
    submitted_at: datetime
    updated_at: datetime
    review_history: list[OrganizationReviewEvent] = Field(default_factory=list)


class OrganizationMapEntry(BaseModel):
    organization_id: str
    organization_name: str
    organization_type: str
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class DaycareDirectoryEntry(BaseModel):
    organization_id: str
    organization_name: str
    organization_type: str
    description: str | None = None
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    contact: str | None = None

class ElderCareDirectoryEntry(BaseModel):
    """Public information for an eligible elder-care home."""

    organization_id: str
    organization_name: str
    organization_type: str

    description: str | None = None
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    contact: str | None = None

    capacity: int
    age_range: str | None = None
    opening_hours: str | None = None
    facilities: str | None = None
    fees: str | None = None
