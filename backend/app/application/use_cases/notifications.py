from app.application.interfaces.notification import (
    NotificationRepository,
)
from app.domain.entities.notification import Notification


class NotificationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    def create_for_users(
        self,
        event_key: str,
        notification_type: str,
        title: str,
        message: str,
        user_ids: list[str],
        organization_id: str | None = None,
    ) -> list[Notification]:
        event_key = event_key.strip()
        notification_type = notification_type.strip()
        title = title.strip()
        message = message.strip()

        if not event_key:
            raise ValueError("An event key is required.")

        if not notification_type or len(notification_type) > 80:
            raise ValueError("Invalid notification type.")

        if not title or len(title) > 200:
            raise ValueError("Notification title must be 1–200 characters.")

        if not message:
            raise ValueError("Notification message cannot be empty.")

        if not user_ids:
            return []

        return self.repository.create_for_users(
            event_key=event_key,
            notification_type=notification_type,
            title=title,
            message=message,
            user_ids=list(set(user_ids)),
            organization_id=organization_id,
        )

    def list_for_user(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
    ) -> list[Notification]:
        if not 1 <= limit <= 100:
            raise ValueError("Limit must be between 1 and 100.")

        return self.repository.list_for_user(
            user_id=user_id,
            unread_only=unread_only,
            limit=limit,
        )

    def mark_as_read(
        self,
        notification_id: str,
        user_id: str,
    ) -> Notification:
        notification = self.repository.mark_as_read(
            notification_id=notification_id,
            user_id=user_id,
        )

        if notification is None:
            raise LookupError("Notification not found.")

        return notification