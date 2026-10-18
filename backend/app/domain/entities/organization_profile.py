from datetime import datetime

from pydantic import BaseModel

from app.domain.entities.organization import OrganizationStatus


class OrganizationProfile(BaseModel):
    organization_id: str
    organization_name: str
    organization_type: str

    description: str | None = None
    location: str | None = None
    contact: str | None = None

    capacity: int = 20
    age_range: str | None = None
    opening_hours: str | None = None
    facilities: str | None = None
    fees: str | None = None

    status: OrganizationStatus
    updated_at: datetime