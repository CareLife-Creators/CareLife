from datetime import datetime

from pydantic import BaseModel

from app.domain.entities.audit_log import AuditLog


class AuditLogResponse(BaseModel):
    id: str
    actor_user_id: str
    actor_role: str
    action: str
    target_type: str
    target_id: str
    created_at: datetime

    @classmethod
    def from_entity(
        cls,
        log: AuditLog,
    ) -> "AuditLogResponse":
        return cls(
            id=log.id,
            actor_user_id=log.actor_user_id,
            actor_role=log.actor_role,
            action=log.action,
            target_type=log.target_type,
            target_id=log.target_id,
            created_at=log.created_at,
        )