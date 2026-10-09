from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel


class DonationNeedType(str, Enum):
    MONETARY = "monetary"
    IN_KIND = "in_kind"


class DonationCampaign(BaseModel):
    id: str
    organization_id: str
    organization_name: str | None = None
    organization_type: str | None = None
    title: str
    description: str | None = None
    target_amount: Decimal
    currency: str
    received_amount: Decimal = Decimal("0.00")
    utilized_amount: Decimal = Decimal("0.00")
    remaining_amount: Decimal = Decimal("0.00")
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class DonationNeed(BaseModel):
    id: str
    organization_id: str
    organization_name: str | None = None
    organization_type: str | None = None
    title: str
    description: str | None = None
    category: str
    need_type: DonationNeedType
    target_amount: Decimal | None = None
    target_quantity: Decimal | None = None
    unit: str | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
