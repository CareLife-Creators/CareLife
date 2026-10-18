from app.application.use_cases.user_profile import UserProfileService
from app.infrastructure.repositories.user_repository import (
    PostgresUserRepository,
)


def get_user_profile_service() -> UserProfileService:
    repository = PostgresUserRepository()

    return UserProfileService(
        repository=repository,
    )