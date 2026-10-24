from datetime import datetime
from typing import Literal

from pydantic import BaseModel


StaffRole = Literal[
    "daycare_staff",
    "orphanage_staff",
    "care_home_staff",
]
RoleRequestStatus = Literal["pending", "approved", "rejected"]


class RoleRequest(BaseModel):
    id: str
    user_id: str
    requested_role: StaffRole
    note: str | None = None
    status: RoleRequestStatus = "pending"
    created_at: datetime
    reviewed_at: datetime | None = None
    reviewed_by: str | None = None
