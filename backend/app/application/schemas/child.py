from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from app.domain.entities.child import (
    ContactType,
    OutcomeStatus,
    OutcomeType,
)


class ChildCreateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)
    date_of_birth: date
    gender: str | None = Field(default=None, max_length=30)
    allergies: str | None = Field(default=None, max_length=1000)
    medical_notes: str | None = Field(default=None, max_length=2000)

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Child name is required")

        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("Date of birth cannot be in the future")

        return value


class ChildUpdateRequest(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )
    date_of_birth: date | None = None
    gender: str | None = Field(
        default=None,
        max_length=30,
    )
    allergies: str | None = Field(
        default=None,
        max_length=1000,
    )
    medical_notes: str | None = Field(
        default=None,
        max_length=2000,
    )

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Child name is required")

        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(
        cls,
        value: date | None,
    ) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("Date of birth cannot be in the future")

        return value


class ChildResponse(BaseModel):
    id: str
    full_name: str
    date_of_birth: date
    gender: str | None
    allergies: str | None
    medical_notes: str | None
    parent_id: str | None
    orphanage_organization_id: str | None
    daycare_organization_id: str | None


class ChildContactRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)
    relationship_to_child: str = Field(
        min_length=2,
        max_length=100,
    )
    phone: str = Field(min_length=7, max_length=30)
    email: str | None = Field(
        default=None,
        max_length=254,
    )
    address: str | None = Field(
        default=None,
        max_length=500,
    )

    @field_validator(
        "full_name",
        "relationship_to_child",
        "phone",
    )
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field is required")

        return value


class ChildContactResponse(BaseModel):
    id: str
    child_id: str
    contact_type: ContactType
    full_name: str
    relationship_to_child: str
    phone: str
    email: str | None
    address: str | None
    created_at: str
    updated_at: str


class OutcomeCreateRequest(BaseModel):
    outcome_type: OutcomeType
    outcome_status: OutcomeStatus = OutcomeStatus.PENDING
    outcome_date: date
    notes: str | None = Field(
        default=None,
        max_length=2000,
    )


class OutcomeUpdateRequest(BaseModel):
    outcome_status: OutcomeStatus
    outcome_date: date
    notes: str | None = Field(
        default=None,
        max_length=2000,
    )


class OutcomeResponse(BaseModel):
    id: str
    child_id: str
    organization_id: str
    outcome_type: OutcomeType
    outcome_status: OutcomeStatus
    outcome_date: date
    notes: str | None
    created_by: str
    created_at: str
    updated_at: str



class AttendanceCheckInRequest(BaseModel):
    enrollment_id: str = Field(
        min_length=1,
        max_length=100,
    )


class AttendanceResponse(BaseModel):
    id: str
    enrollment_id: str
    attendance_date: date
    check_in_at: datetime
    check_out_at: datetime | None
    recorded_by: str




class DailyUpdateCreateRequest(BaseModel):
    notes: str = Field(
        min_length=1,
        max_length=2000,
    )

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Daily update notes are required")

        return value


class DailyUpdateResponse(BaseModel):
    id: str
    child_id: str
    daycare_organization_id: str
    update_date: date
    notes: str
    recorded_by: str
    created_at: datetime