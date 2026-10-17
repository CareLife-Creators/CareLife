from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from app.domain.entities.in_kind_donation import (
    InKindDonationStatus,
)


class InKindDonationPledgeCreateRequest(BaseModel):
    quantity: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=3,
    )
    notes: str | None = Field(
        default=None,
        max_length=1000,
    )

    @field_validator("notes")
    @classmethod
    def clean_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return value.strip() or None


class InKindDonationStatusUpdateRequest(BaseModel):
    status: InKindDonationStatus

    @field_validator("status")
    @classmethod
    def validate_next_status(
        cls,
        value: InKindDonationStatus,
    ) -> InKindDonationStatus:
        if value == InKindDonationStatus.PLEDGED:
            raise ValueError(
                "A pledge cannot be moved back to pledged status"
            )

        return value


class InKindDonationPledgeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    need_id: str
    need_title: str
    organization_id: str
    organization_name: str
    donor_id: str
    quantity: Decimal
    unit: str
    notes: str | None
    status: InKindDonationStatus
    received_by: str | None
    received_at: datetime | None
    allocated_by: str | None
    allocated_at: datetime | None
    created_at: datetime
    updated_at: datetime