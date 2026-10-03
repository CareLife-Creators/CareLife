from datetime import date

from pydantic import BaseModel, Field, field_validator


class OrganizationRegistrationRequest(BaseModel):
    organization_name: str = Field(min_length=2, max_length=200)
    organization_type: str = Field(min_length=2, max_length=100)
    license_number: str = Field(min_length=1, max_length=100)
    license_expiry_date: date

    @field_validator(
        "organization_name",
        "organization_type",
        "license_number",
        mode="before",
    )
    @classmethod
    def strip_required_text(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("This field is required.")
        return value

    @field_validator("license_expiry_date")
    @classmethod
    def validate_license_expiry(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("License expiry date cannot be in the past.")
        return value
