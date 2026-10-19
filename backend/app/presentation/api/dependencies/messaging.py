from app.application.use_cases.messaging import MessagingService
from app.infrastructure.repositories.messaging import (
    PostgresMessagingRepository,
)


def get_messaging_service() -> MessagingService:
    return MessagingService(
        PostgresMessagingRepository()
    )