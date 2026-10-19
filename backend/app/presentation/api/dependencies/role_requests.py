from app.application.use_cases.role_requests import RoleRequestService
from app.infrastructure.repositories.role_request_repository import (
    PostgresRoleRequestRepository,
)


def get_role_request_service() -> RoleRequestService:
    return RoleRequestService(
        repository=PostgresRoleRequestRepository(),
    )
