from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.domain.entities.remote_checkin import (
    RemoteCheckIn,
    ResidentConsent,
    ResidentConsentStatus,
    WellbeingStatus,
)


class ConsentUpdateRequest(BaseModel):
    family_representative_id: str = Field(
        min_length=1,
        max_length=100,
    )
    consent_granted: bool

    @field_validator("family_representative_id")
    @classmethod
    def validate_representative_id(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Family representative ID is required"
            )

        return value


class ResidentConsentResponse(BaseModel):
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

    @classmethod
    def from_entity(
        cls,
        entity: ResidentConsent,
    ) -> "ResidentConsentResponse":
        return cls(**entity.model_dump())


class RemoteCheckInCreateRequest(BaseModel):
    wellbeing_status: WellbeingStatus

    notes: str | None = Field(
        default=None,
        max_length=2000,
    )

    @field_validator("notes")
    @classmethod
    def clean_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None


class RemoteCheckInResponse(BaseModel):
    id: str
    consent_id: str
    resident_id: str
    organization_id: str
    actor_user_id: str
    wellbeing_status: WellbeingStatus
    notes: str | None = None
    recorded_at: datetime

    @classmethod
    def from_entity(
        cls,
        entity: RemoteCheckIn,
    ) -> "RemoteCheckInResponse":
        return cls(**entity.model_dump())