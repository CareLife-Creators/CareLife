from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.domain.entities.organization import OrganizationStatus


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
    contact: str | None = Field(default=None, max_length=100)

    license_number: str = Field(
        min_length=1,
        max_length=100,
    )

    license_expiry_date: date

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


class OrganizationVerificationDecisionRequest(BaseModel):
    message: str | None = None


class DaycareDirectoryResponse(BaseModel):
    organization_id: str
    organization_name: str
    organization_type: str
    description: str | None = None
    location: str | None = None
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
            contact=organization.contact,
        )