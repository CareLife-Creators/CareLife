from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.domain.entities.donation import DonationNeedType


class DonationCampaignCreateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    target_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="BDT", min_length=3, max_length=3)
    is_active: bool = True

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Campaign title is required")
        return value

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip().upper()
            if len(value) != 3 or not value.isalpha():
                raise ValueError("Currency must be a three-letter code")
        return value


class DonationCampaignUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    target_amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    utilized_amount: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    is_active: bool | None = None

    @model_validator(mode="after")
    def require_change(self) -> "DonationCampaignUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("At least one campaign field must be supplied")
        return self

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Campaign title is required")
        return value

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip().upper()
            if len(value) != 3 or not value.isalpha():
                raise ValueError("Currency must be a three-letter code")
        return value


class DonationNeedCreateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    category: str = Field(min_length=2, max_length=100)
    need_type: DonationNeedType
    target_amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    target_quantity: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=3)
    unit: str | None = Field(default=None, max_length=50)
    is_active: bool = True

    @field_validator("title", "category")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field is required")
        return value

    @field_validator("description", "unit")
    @classmethod
    def clean_optional_text(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None

    @model_validator(mode="after")
    def validate_target_for_need_type(self) -> "DonationNeedCreateRequest":
        if self.need_type == DonationNeedType.MONETARY:
            if self.target_amount is None:
                raise ValueError("A monetary need requires target_amount")
            if self.target_quantity is not None or self.unit is not None:
                raise ValueError("A monetary need must not include target_quantity or unit")
        else:
            if self.target_quantity is None or not self.unit:
                raise ValueError("An in-kind need requires target_quantity and unit")
            if self.target_amount is not None:
                raise ValueError("An in-kind need must not include target_amount")
        return self


class DonationNeedUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    category: str | None = Field(default=None, min_length=2, max_length=100)
    need_type: DonationNeedType | None = None
    target_amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    target_quantity: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=3)
    unit: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None

    @model_validator(mode="after")
    def require_change(self) -> "DonationNeedUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("At least one donation-need field must be supplied")
        return self

    @field_validator("title", "category")
    @classmethod
    def validate_required_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("This field is required")
        return value

    @field_validator("description", "unit")
    @classmethod
    def clean_optional_text(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None


class DonationCampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    organization_name: str
    organization_type: str
    title: str
    description: str | None
    target_amount: Decimal
    received_amount: Decimal
    utilized_amount: Decimal
    remaining_amount: Decimal
    currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DonationNeedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    organization_name: str
    organization_type: str
    title: str
    description: str | None
    category: str
    need_type: DonationNeedType
    target_amount: Decimal | None
    target_quantity: Decimal | None
    unit: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
