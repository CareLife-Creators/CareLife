from datetime import date

from pydantic import BaseModel, Field, field_validator

from app.domain.entities.child import OutcomeStatus, OutcomeType


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
    full_name: str | None = Field(default=None, min_length=2, max_length=200)
    gender: str | None = Field(default=None, max_length=30)
    allergies: str | None = Field(default=None, max_length=1000)
    medical_notes: str | None = Field(default=None, max_length=2000)

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Child name is required")
        return value


class ChildResponse(BaseModel):
    id: str
    full_name: str
    date_of_birth: date
    gender: str | None
    allergies: str | None
    medical_notes: str | None
    orphanage_organization_id: str | None


class OutcomeCreateRequest(BaseModel):
    outcome_type: OutcomeType
    outcome_status: OutcomeStatus = OutcomeStatus.PENDING
    outcome_date: date
    notes: str | None = Field(default=None, max_length=2000)


class OutcomeUpdateRequest(BaseModel):
    outcome_status: OutcomeStatus
    outcome_date: date
    notes: str | None = Field(default=None, max_length=2000)


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
