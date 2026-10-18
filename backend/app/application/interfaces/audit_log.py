from typing import Protocol

from app.domain.entities.audit_log import AuditLog


class AuditLogRepository(Protocol):

    def list_logs(
        self,
        limit: int,
        offset: int,
    ) -> list[AuditLog]:
        ...