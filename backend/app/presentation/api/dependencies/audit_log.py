from app.application.use_cases.audit_log import AuditLogService
from app.infrastructure.repositories.audit_log_repository import (
    PostgresAuditLogRepository,
)


def get_audit_log_service() -> AuditLogService:
    repository = PostgresAuditLogRepository()

    return AuditLogService(
        repository=repository,
    )