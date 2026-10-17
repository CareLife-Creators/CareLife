import re
from datetime import date

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.domain.entities.resident import (
    ResidentProfile,
    ResidentProfileStatus,
)


class ResidentProfileCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(min_length=1, max_length=150)

    preferred_name: str | None = Field(
        default=None,
        max_length=100,
    )

    date_of_birth: date | None = None

    room_number: str | None = Field(
        default=None,
        max_length=50,
    )

    emergency_contact_name: str | None = Field(
        default=None,
        max_length=150,
    )

    emergency_contact_phone: str | None = Field(
        default=None,
        max_length=30,
    )

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Resident name is required")

        return value

    @field_validator(
        "preferred_name",
        "room_number",
        "emergency_contact_name",
    )
    @classmethod
    def clean_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None

    @field_validator("emergency_contact_phone")
    @classmethod
    def validate_phone(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        if not re.fullmatch(r"[0-9+().\-\s]{7,30}", value):
            raise ValueError(
                "Emergency contact phone contains invalid characters"
            )

        if sum(character.isdigit() for character in value) < 7:
            raise ValueError(
                "Emergency contact phone must contain at least "
                "7 digits"
            )

        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(
        cls,
        value: date | None,
    ) -> date | None:
        if value is not None and value > date.today():
            raise ValueError(
                "Date of birth cannot be in the future"
            )

        return value

    @model_validator(mode="after")
    def validate_emergency_contact(self):
        has_name = self.emergency_contact_name is not None
        has_phone = self.emergency_contact_phone is not None

        if has_name != has_phone:
            raise ValueError(
                "Emergency contact name and phone must be "
                "provided together"
            )

        return self


class ResidentProfileUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    preferred_name: str | None = Field(
        default=None,
        max_length=100,
    )

    date_of_birth: date | None = None

    room_number: str | None = Field(
        default=None,
        max_length=50,
    )

    emergency_contact_name: str | None = Field(
        default=None,
        max_length=150,
    )

    emergency_contact_phone: str | None = Field(
        default=None,
        max_length=30,
    )

    status: ResidentProfileStatus | None = None

    @field_validator("full_name")
    @classmethod
    def validate_full_name(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Resident name cannot be empty")

        return value

    @field_validator(
        "preferred_name",
        "room_number",
        "emergency_contact_name",
    )
    @classmethod
    def clean_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None

    @field_validator("emergency_contact_phone")
    @classmethod
    def validate_phone(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        if not re.fullmatch(r"[0-9+().\-\s]{7,30}", value):
            raise ValueError(
                "Emergency contact phone contains invalid characters"
            )

        if sum(character.isdigit() for character in value) < 7:
            raise ValueError(
                "Emergency contact phone must contain at least "
                "7 digits"
            )

        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(
        cls,
        value: date | None,
    ) -> date | None:
        if value is not None and value > date.today():
            raise ValueError(
                "Date of birth cannot be in the future"
            )

        return value


class ResidentProfileResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    organization_id: str
    full_name: str
    preferred_name: str | None = None
    date_of_birth: date | None = None
    room_number: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    status: ResidentProfileStatus
    created_by: str
    updated_by: str
    created_at: object
    updated_at: object

    @classmethod
    def from_entity(
        cls,
        entity: ResidentProfile,
    ) -> "ResidentProfileResponse":
        return cls(**entity.model_dump())