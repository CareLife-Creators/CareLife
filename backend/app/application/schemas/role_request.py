from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


StaffRole = Literal[
    "daycare_staff",
    "orphanage_staff",
    "care_home_staff",
]
RoleRequestStatus = Literal["pending", "approved", "rejected"]


class RoleRequestCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requested_role: StaffRole
    note: str | None = Field(default=None, max_length=1000)

    @field_validator("note", mode="before")
    @classmethod
    def normalize_note(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class RoleRequestResponse(BaseModel):
    id: str
    user_id: str
    requested_role: StaffRole
    note: str | None = None
    status: RoleRequestStatus
    created_at: datetime
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None
