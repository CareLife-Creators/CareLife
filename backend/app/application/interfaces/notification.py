from typing import Protocol

from app.domain.entities.notification import Notification


class NotificationRepository(Protocol):
    def create_for_users(
        self,
        event_key: str,
        notification_type: str,
        title: str,
        message: str,
        user_ids: list[str],
        organization_id: str | None = None,
    ) -> list[Notification]:
        ...

    def list_for_user(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
    ) -> list[Notification]:
        ...

    def mark_as_read(
        self,
        notification_id: str,
        user_id: str,
    ) -> Notification | None:
        ...