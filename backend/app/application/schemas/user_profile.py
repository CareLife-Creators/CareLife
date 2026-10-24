import re

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


class UserProfileUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(
        default=None,
        max_length=200,
    )
    phone: str | None = Field(
        default=None,
        max_length=30,
    )

    @field_validator("full_name", "phone", mode="before")
    @classmethod
    def normalize_optional_text(cls, value):
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()
            return value or None

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if value is None:
            return None

        if not re.fullmatch(r"[+()\d.\-\s]+", value):
            raise ValueError(
                "Phone number contains unsupported characters."
            )

        digit_count = len(re.sub(r"\D", "", value))

        if not 7 <= digit_count <= 15:
            raise ValueError(
                "Phone number must contain between 7 and 15 digits."
            )

        return value

    @model_validator(mode="after")
    def require_at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError(
                "Provide at least one profile field to update."
            )

        return self


class UserProfileResponse(BaseModel):
    user_id: str
    email: EmailStr
    full_name: str | None = None
    phone: str | None = None
    role: str
    profile_photo_url: str | None = None
