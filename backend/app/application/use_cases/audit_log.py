from app.application.interfaces.audit_log import (
    AuditLogRepository,
)
from app.domain.entities.audit_log import AuditLog


class AuditLogService:

    def __init__(
        self,
        repository: AuditLogRepository,
    ):
        self.repository = repository

    def list_logs(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditLog]:
        return self.repository.list_logs(
            limit=limit,
            offset=offset,
        )