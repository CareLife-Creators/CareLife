from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel


class OutcomeType(str, Enum):
    ADOPTION = "adoption"
    GUARDIANSHIP = "guardianship"


class OutcomeStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Child(BaseModel):
    id: str
    parent_id: str | None
    full_name: str
    date_of_birth: date
    gender: str | None
    allergies: str | None
    medical_notes: str | None
    orphanage_organization_id: str | None
    daycare_organization_id: str | None
    created_at: datetime
    updated_at: datetime

