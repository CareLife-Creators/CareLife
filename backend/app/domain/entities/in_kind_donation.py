from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel


class InKindDonationStatus(str, Enum):
    PLEDGED = "pledged"
    RECEIVED = "received"
    ALLOCATED = "allocated"


class InKindDonationPledge(BaseModel):
    id: str
    need_id: str
    need_title: str | None = None
    organization_id: str | None = None
    organization_name: str | None = None
    donor_id: str
    quantity: Decimal
    unit: str | None = None
    notes: str | None = None
    status: InKindDonationStatus = InKindDonationStatus.PLEDGED
    received_by: str | None = None
    received_at: datetime | None = None
    allocated_by: str | None = None
    allocated_at: datetime | None = None
    created_at: datetime
    updated_at: datetime