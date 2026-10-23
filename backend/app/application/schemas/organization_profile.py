from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.domain.entities.organization import OrganizationStatus
from app.domain.entities.organization_profile import (
    OrganizationProfile,
)


class OrganizationProfileUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    organization_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )

    latitude: float | None = Field(default=None, ge=20.5, le=26.8)
    longitude: float | None = Field(default=None, ge=88.0, le=92.8)

    contact: str | None = Field(
        default=None,
        max_length=100,
    )

    capacity: int | None = Field(
        default=None,
        ge=0,
    )

    age_range: str | None = Field(
        default=None,
        max_length=100,
    )

    opening_hours: str | None = Field(
        default=None,
        max_length=255,
    )

    facilities: str | None = Field(
        default=None,
        max_length=5000,
    )

    fees: str | None = Field(
        default=None,
        max_length=2000,
    )

    @field_validator(
        "organization_name",
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
    def normalize_text(
        cls,
        value: object,
    ) -> object:
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()
            return value or None

        return value

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_fields_set:
            raise ValueError(
                "Provide at least one organization field to update."
            )

        if (
            "organization_name" in self.model_fields_set
            and self.organization_name is None
        ):
            raise ValueError(
                "Organization name cannot be empty."
            )

        if (
            "capacity" in self.model_fields_set
            and self.capacity is None
        ):
            raise ValueError(
                "Capacity cannot be null."
            )

        if ("latitude" in self.model_fields_set or "longitude" in self.model_fields_set):
            if not {"latitude", "longitude"}.issubset(self.model_fields_set):
                raise ValueError("Provide both map coordinates, or clear both.")
            if (self.latitude is None) != (self.longitude is None):
                raise ValueError("Provide both map coordinates, or clear both.")

        return self


class OrganizationProfileResponse(BaseModel):
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

    status: OrganizationStatus
    updated_at: datetime

    @classmethod
    def from_entity(
        cls,
        profile: OrganizationProfile,
    ) -> "OrganizationProfileResponse":
        return cls(
            organization_id=profile.organization_id,
            organization_name=profile.organization_name,
            organization_type=profile.organization_type,
            description=profile.description,
            location=profile.location,
            latitude=profile.latitude,
            longitude=profile.longitude,
            contact=profile.contact,
            capacity=profile.capacity,
            age_range=profile.age_range,
            opening_hours=profile.opening_hours,
            facilities=profile.facilities,
            fees=profile.fees,
            status=profile.status,
            updated_at=profile.updated_at,
        )


class PublicOrganizationProfileResponse(BaseModel):
    """Fields that are safe to return in a public profile."""

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
        profile: OrganizationProfile,
    ) -> "PublicOrganizationProfileResponse":
        return cls(
            organization_id=profile.organization_id,
            organization_name=profile.organization_name,
            organization_type=profile.organization_type,
            description=profile.description,
            location=profile.location,
            latitude=profile.latitude,
            longitude=profile.longitude,
            contact=profile.contact,
            capacity=profile.capacity,
            age_range=profile.age_range,
            opening_hours=profile.opening_hours,
            facilities=profile.facilities,
            fees=profile.fees,
        )


class PublicOrphanageProfileResponse(
    PublicOrganizationProfileResponse
):
    """
    Public orphanage profile.

    Includes a verification badge while excluding internal
    verification records, license details, and user records.
    """

    verification_status: OrganizationStatus

    @classmethod
    def from_entity(
        cls,
        profile: OrganizationProfile,
    ) -> "PublicOrphanageProfileResponse":
        public_profile = (
            PublicOrganizationProfileResponse.from_entity(
                profile
            )
        )

        return cls(
            **public_profile.model_dump(),
            verification_status=profile.status,
        )
