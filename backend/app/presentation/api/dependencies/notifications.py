from app.application.use_cases.notifications import NotificationService
from app.infrastructure.repositories.notifications import (
    PostgresNotificationRepository,
)


def get_notification_service() -> NotificationService:
    return NotificationService(
        PostgresNotificationRepository()
    )