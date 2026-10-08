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


class ContactType(str, Enum):
    EMERGENCY = "emergency"
    PICKUP = "pickup"


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


class ChildContact(BaseModel):
    id: str
    child_id: str
    contact_type: ContactType
    full_name: str
    relationship_to_child: str
    phone: str
    email: str | None
    address: str | None
    created_by: str
    created_at: datetime
    updated_at: datetime


class OrphanageOutcome(BaseModel):
    id: str
    child_id: str
    organization_id: str
    outcome_type: OutcomeType
    outcome_status: OutcomeStatus
    outcome_date: date
    notes: str | None
    created_by: str
    created_at: datetime
    updated_at: datetime