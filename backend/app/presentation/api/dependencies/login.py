from app.application.use_cases.login import LoginService
from app.infrastructure.repositories.user_repository import (
    PostgresUserRepository,
)


def get_login_service() -> LoginService:
    repository = PostgresUserRepository()
    return LoginService(repository=repository)