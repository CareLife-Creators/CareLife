from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.domain.entities.elder_care_booking import (
    ElderCareBooking,
    ElderCareBookingStatusHistory,
    ElderCareProviderType,
)


class ElderCareBookingCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resident_id: str = Field(min_length=1, max_length=100)

    provider_type: ElderCareProviderType
    provider_id: str = Field(min_length=1, max_length=100)

    service_type: str = Field(min_length=2, max_length=100)

    starts_at: datetime
    ends_at: datetime

    message: str | None = Field(
        default=None,
        max_length=1000,
    )

    @field_validator("resident_id", "provider_id")
    @classmethod
    def clean_ids(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("An identifier is required")

        return value

    @field_validator("service_type")
    @classmethod
    def clean_service_type(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 2:
            raise ValueError("Service type is required")

        return value

    @field_validator("message")
    @classmethod
    def clean_message(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def validate_time_range(self):
        if (
            self.starts_at.tzinfo is None
            or self.ends_at.tzinfo is None
        ):
            raise ValueError(
                "Start and end times must include a timezone"
            )

        if self.ends_at <= self.starts_at:
            raise ValueError(
                "End time must be later than start time"
            )

        return self


class ElderCareBookingDecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["approved", "rejected"]

    note: str | None = Field(
        default=None,
        max_length=1000,
    )

    @field_validator("note")
    @classmethod
    def clean_note(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None


class ElderCareBookingNoteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    note: str | None = Field(
        default=None,
        max_length=1000,
    )

    @field_validator("note")
    @classmethod
    def clean_note(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None


class ElderCareBookingResponse(BaseModel):
    id: str
    resident_id: str
    requester_user_id: str

    provider_type: ElderCareProviderType
    provider_id: str

    caregiver_user_id: str | None = None
    organization_id: str | None = None
    availability_id: str | None = None

    service_type: str
    starts_at: datetime
    ends_at: datetime

    status: str
    message: str | None = None
    decision_message: str | None = None
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    cancelled_by: str | None = None
    completed_at: datetime | None = None

    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(
        cls,
        booking: ElderCareBooking,
    ) -> "ElderCareBookingResponse":
        return cls(
            id=booking.id,
            resident_id=booking.resident_id,
            requester_user_id=booking.requester_user_id,
            provider_type=booking.provider_type,
            provider_id=booking.provider_id,
            caregiver_user_id=booking.caregiver_user_id,
            organization_id=booking.organization_id,
            availability_id=booking.availability_id,
            service_type=booking.service_type,
            starts_at=booking.starts_at,
            ends_at=booking.ends_at,
            status=booking.status.value,
            message=booking.message,
            decision_message=booking.decision_message,
            reviewed_by=booking.reviewed_by,
            reviewed_at=booking.reviewed_at,
            cancelled_by=booking.cancelled_by,
            completed_at=booking.completed_at,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
        )


class ElderCareBookingStatusHistoryResponse(BaseModel):
    id: str
    booking_id: str
    sequence_no: int
    from_status: str | None = None
    to_status: str
    changed_by: str | None = None
    note: str | None = None
    created_at: datetime

    @classmethod
    def from_entity(
        cls,
        item: ElderCareBookingStatusHistory,
    ) -> "ElderCareBookingStatusHistoryResponse":
        return cls(
            id=item.id,
            booking_id=item.booking_id,
            sequence_no=item.sequence_no,
            from_status=(
                item.from_status.value
                if item.from_status is not None
                else None
            ),
            to_status=item.to_status.value,
            changed_by=item.changed_by,
            note=item.note,
            created_at=item.created_at,
        )