from fastapi import APIRouter, Depends, Query

from app.application.schemas.audit_log import AuditLogResponse
from app.application.use_cases.audit_log import AuditLogService
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.audit_log import (
    get_audit_log_service,
)
from app.presentation.api.dependencies.authorization import (
    require_role,
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin Audit Logs"],
)


@router.get(
    "/audit-logs",
    response_model=list[AuditLogResponse],
)
def get_audit_logs(
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    _current_user: UserContext = Depends(
        require_role(Role.CARELIFE_ADMIN)
    ),
    service: AuditLogService = Depends(
        get_audit_log_service
    ),
) -> list[AuditLogResponse]:
    logs = service.list_logs(
        limit=limit,
        offset=offset,
    )

    return [
        AuditLogResponse.from_entity(log)
        for log in logs
    ]