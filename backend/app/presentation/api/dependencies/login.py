from app.application.use_cases.login import LoginService
from app.infrastructure.repositories.password_reset_repository import (
    PostgresPasswordResetRepository,
)


def get_login_service() -> LoginService:
    return LoginService(
        repository=PostgresPasswordResetRepository()
    )
