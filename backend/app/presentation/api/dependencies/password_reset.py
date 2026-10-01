from app.application.use_cases.password_reset import PasswordResetService
from app.core.config import get_settings
from app.infrastructure.email.password_reset_email import (
    build_password_reset_email_sender,
)
from app.infrastructure.repositories.password_reset_repository import (
    PostgresPasswordResetRepository,
)


def get_password_reset_service() -> PasswordResetService:
    settings = get_settings()

    repository = PostgresPasswordResetRepository()

    email_sender = build_password_reset_email_sender(settings)

    return PasswordResetService(
        repository=repository,
        email_sender=email_sender,
        token_expire_minutes=settings.reset_token_expire_minutes,
        reset_link_base_url=settings.reset_link_base_url,
    )