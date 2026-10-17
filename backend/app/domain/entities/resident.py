from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class ResidentProfileStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ResidentProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    organization_id: str
    full_name: str
    preferred_name: str | None = None
    date_of_birth: date | None = None
    room_number: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    status: ResidentProfileStatus
    created_by: str
    updated_by: str
    created_at: datetime
    updated_at: datetime