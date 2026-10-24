from datetime import datetime

from pydantic import BaseModel


class AuditLog(BaseModel):
    id: str
    actor_user_id: str
    actor_role: str
    action: str
    target_type: str
    target_id: str
    created_at: datetime