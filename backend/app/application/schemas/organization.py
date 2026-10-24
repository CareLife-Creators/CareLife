from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.domain.entities.organization import (
    ElderCareDirectoryEntry,
    OrganizationStatus,
)

class OrganizationRegistrationRequest(BaseModel):

    organization_name: str = Field(
        min_length=2,
        max_length=200,
    )

    organization_type: Literal[
        "daycare",
        "orphanage",
        "elderly_care",
    ]

    description: str | None = Field(default=None, max_length=5000)
    location: str | None = Field(default=None, max_length=255)
    latitude: float | None = Field(default=None, ge=20.5, le=26.8)
    longitude: float | None = Field(default=None, ge=88.0, le=92.8)
    contact: str | None = Field(default=None, max_length=100)
    capacity: int = Field(default=20, ge=0, le=100000)
    age_range: str | None = Field(default=None, max_length=100)
    opening_hours: str | None = Field(default=None, max_length=255)
    facilities: str | None = Field(default=None, max_length=5000)
    fees: str | None = Field(default=None, max_length=2000)

    license_number: str = Field(
        min_length=1,
        max_length=100,
    )

    license_expiry_date: date

    @model_validator(mode="after")
    def coordinates_are_a_pair(self):
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("Provide both map coordinates, or leave both empty.")
        return self

    @field_validator(
        "organization_name",
        "license_number",
        mode="before",
    )
    @classmethod
    def strip_required_text(
        cls,
        value: object,
    ) -> object:

        if isinstance(value, str):
            value = value.strip()

            if not value:
                raise ValueError(
                    "This field is required."
                )

        return value

    @field_validator(
        "description",
        "location",
        "contact",
        "age_range",
        "opening_hours",
        "facilities",
        "fees",
        mode="before",
    )
    @classmethod
    def strip_optional_text(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @field_validator("license_expiry_date")
    @classmethod
    def validate_license_expiry(
        cls,
        value: date,
    ) -> date:

        if value < date.today():
            raise ValueError(
                "License expiry date cannot be in the past."
            )

        return value


class OrganizationVerificationResponse(BaseModel):
    organization_id: str
    organization_name: str
    organization_type: str
    description: str | None = None
    location: str | None = None
    contact: str | None = None
    license_number: str
    license_expiry_date: date
    submitted_by: str
    status: OrganizationStatus
    submitted_at: datetime
    updated_at: datetime
    message: str | None = None


class OrganizationApplicantApplicationResponse(BaseModel):
    organization_id: str
    organization_name: str
    organization_type: str
    status: OrganizationStatus
    submitted_at: datetime
    updated_at: datetime
    message: str | None = None

    @classmethod
    def from_entity(cls, organization):
        return cls(
            organization_id=organization.organization_id,
            organization_name=organization.organization_name,
            organization_type=organization.organization_type,
            status=organization.status,
            submitted_at=organization.submitted_at,
            updated_at=organization.updated_at,
            message=organization.message,
        )


class OrganizationVerificationDecisionRequest(BaseModel):
    message: str | None = None


class OrganizationReviewEventResponse(BaseModel):
    status: OrganizationStatus
    reviewer_name: str | None = None
    notes: str | None = None
    reviewed_at: datetime


class OrganizationTrackingResponse(BaseModel):
    organization_id: str
    organization_name: str
    organization_type: str
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    status: OrganizationStatus
    submitted_at: datetime
    updated_at: datetime
    review_history: list[OrganizationReviewEventResponse] = Field(default_factory=list)


class OrganizationMapEntryResponse(BaseModel):
    organization_id: str
    organization_name: str
    organization_type: str
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class DaycareDirectoryResponse(BaseModel):
    organization_id: str
    organization_name: str
    organization_type: str
    description: str | None = None
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    contact: str | None = None

    @classmethod
    def from_entity(
        cls,
        organization,
    ) -> "DaycareDirectoryResponse":

        return cls(
            organization_id=organization.organization_id,
            organization_name=organization.organization_name,
            organization_type=organization.organization_type,
            description=organization.description,
            location=organization.location,
            latitude=organization.latitude,
            longitude=organization.longitude,
            contact=organization.contact,
        )


class ElderCareDirectoryResponse(BaseModel):
    """Public response returned by the elder-care directory."""

    organization_id: str
    organization_name: str
    organization_type: str

    description: str | None = None
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    contact: str | None = None

    capacity: int
    age_range: str | None = None
    opening_hours: str | None = None
    facilities: str | None = None
    fees: str | None = None

    @classmethod
    def from_entity(
        cls,
        organization: ElderCareDirectoryEntry,
    ) -> "ElderCareDirectoryResponse":
        return cls(
            organization_id=organization.organization_id,
            organization_name=organization.organization_name,
            organization_type=organization.organization_type,
            description=organization.description,
            location=organization.location,
            latitude=organization.latitude,
            longitude=organization.longitude,
            contact=organization.contact,
            capacity=organization.capacity,
            age_range=organization.age_range,
            opening_hours=organization.opening_hours,
            facilities=organization.facilities,
            fees=organization.fees,
        )
