from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class ElderCareProviderType(str, Enum):
    CAREGIVER = "caregiver"
    CARE_HOME = "care_home"


class ElderCareBookingStatus(str, Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class ElderCareBooking(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    resident_id: str
    resident_organization_id: str
    requester_user_id: str

    provider_type: ElderCareProviderType
    caregiver_user_id: str | None = None
    organization_id: str | None = None
    availability_id: str | None = None

    service_type: str
    starts_at: datetime
    ends_at: datetime

    status: ElderCareBookingStatus
    message: str | None = None
    decision_message: str | None = None
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    cancelled_by: str | None = None
    completed_at: datetime | None = None

    created_at: datetime
    updated_at: datetime

    @property
    def provider_id(self) -> str:
        if self.provider_type == ElderCareProviderType.CAREGIVER:
            return self.caregiver_user_id or ""

        return self.organization_id or ""


class ElderCareBookingStatusHistory(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    booking_id: str
    sequence_no: int
    from_status: ElderCareBookingStatus | None = None
    to_status: ElderCareBookingStatus
    changed_by: str | None = None
    note: str | None = None
    created_at: datetime