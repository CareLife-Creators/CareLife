from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ResidentConsentStatus(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"


class WellbeingStatus(str, Enum):
    WELL = "well"
    NEEDS_ATTENTION = "needs_attention"
    URGENT = "urgent"


class ResidentConsent(BaseModel):
    id: str
    resident_id: str
    organization_id: str
    family_representative_id: str
    status: ResidentConsentStatus
    granted_by: str | None = None
    granted_at: datetime | None = None
    revoked_by: str | None = None
    revoked_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class RemoteCheckIn(BaseModel):
    id: str
    consent_id: str
    resident_id: str
    organization_id: str
    actor_user_id: str
    wellbeing_status: WellbeingStatus
    notes: str | None = None
    recorded_at: datetime