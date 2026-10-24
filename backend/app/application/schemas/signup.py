import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


PublicSignupRole = Literal[
    "parent_guardian",
    "donor_supporter",
    "independent_caregiver",
    "family_representative",
]


class SignupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=1, max_length=200)
    phone: str = Field(min_length=7, max_length=30)
    role: PublicSignupRole

    @field_validator("full_name", mode="before")
    @classmethod
    def normalize_full_name(cls, value):
        if isinstance(value, str):
            value = value.strip()
            if value:
                return value
        raise ValueError("Full name is required")

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value):
        if not isinstance(value, str):
            return value
        return value.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if not re.fullmatch(r"[+()\d.\-\s]+", value):
            raise ValueError("Phone number contains unsupported characters.")
        digit_count = len(re.sub(r"\D", "", value))
        if not 7 <= digit_count <= 15:
            raise ValueError(
                "Phone number must contain between 7 and 15 digits."
            )
        return value


class SignupResponse(BaseModel):
    message: str
