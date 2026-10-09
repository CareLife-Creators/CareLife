from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class EnrollmentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    WAITLISTED = "waitlisted"
    CANCELLED = "cancelled"


class Enrollment(BaseModel):
    id: str
    child_id: str
    daycare_organization_id: str
    status: EnrollmentStatus

    requested_at: datetime

    reviewed_at: datetime | None = None
    reviewed_by: str | None = None

    cancelled_at: datetime | None = None
    decision_message: str | None = None