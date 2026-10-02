from app.application.use_cases.signup import SignupService
from app.infrastructure.repositories.user_repository import (
    PostgresUserRepository,
)


def get_signup_service() -> SignupService:
    repository = PostgresUserRepository()
    return SignupService(repository=repository)