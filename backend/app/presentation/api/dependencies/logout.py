from app.application.use_cases.logout import LogoutService
from app.infrastructure.repositories.session_repository import (
    PostgresSessionRepository,
)


def get_logout_service() -> LogoutService:
    repository = PostgresSessionRepository()
    return LogoutService(repository=repository)