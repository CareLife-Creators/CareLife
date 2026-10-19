from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.domain.entities.caregiver_booking import (
    CaregiverAppointment,
    CaregiverAvailability,
)


class CaregiverAvailabilityCreateRequest(BaseModel):
    starts_at: datetime
    ends_at: datetime

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.starts_at.tzinfo is None or self.ends_at.tzinfo is None:
            raise ValueError(
                "Start and end times must include a timezone."
            )

        if self.ends_at <= self.starts_at:
            raise ValueError(
                "End time must be later than start time."
            )

        return self


class CaregiverAppointmentCreateRequest(BaseModel):
    availability_id: str = Field(
        min_length=1,
        max_length=100,
    )
    message: str | None = Field(
        default=None,
        max_length=1000,
    )


class CaregiverAppointmentDecisionRequest(BaseModel):
    status: Literal["accepted", "rejected"]
    message: str | None = Field(
        default=None,
        max_length=1000,
    )


class CaregiverAvailabilityResponse(BaseModel):
    id: str
    caregiver_user_id: str
    starts_at: datetime
    ends_at: datetime
    created_at: datetime

    @classmethod
    def from_entity(
        cls,
        slot: CaregiverAvailability,
    ) -> "CaregiverAvailabilityResponse":
        return cls(
            id=slot.id,
            caregiver_user_id=slot.caregiver_user_id,
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            created_at=slot.created_at,
        )


class CaregiverAppointmentResponse(BaseModel):
    id: str
    availability_id: str
    caregiver_user_id: str
    requester_user_id: str
    service_type: str
    starts_at: datetime
    ends_at: datetime
    status: str
    message: str | None = None
    decision_message: str | None = None
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(
        cls,
        appointment: CaregiverAppointment,
    ) -> "CaregiverAppointmentResponse":
        return cls(
            id=appointment.id,
            availability_id=appointment.availability_id,
            caregiver_user_id=appointment.caregiver_user_id,
            requester_user_id=appointment.requester_user_id,
            service_type=appointment.service_type,
            starts_at=appointment.starts_at,
            ends_at=appointment.ends_at,
            status=appointment.status.value,
            message=appointment.message,
            decision_message=appointment.decision_message,
            reviewed_by=appointment.reviewed_by,
            reviewed_at=appointment.reviewed_at,
            created_at=appointment.created_at,
            updated_at=appointment.updated_at,
        )