from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class CaregiverAppointmentStatus(str, Enum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class CaregiverAvailability(BaseModel):
    id: str
    caregiver_user_id: str
    starts_at: datetime
    ends_at: datetime
    created_at: datetime


class CaregiverAppointment(BaseModel):
    id: str
    availability_id: str
    caregiver_user_id: str
    requester_user_id: str
    service_type: str
    starts_at: datetime
    ends_at: datetime
    status: CaregiverAppointmentStatus
    message: str | None = None
    decision_message: str | None = None
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime