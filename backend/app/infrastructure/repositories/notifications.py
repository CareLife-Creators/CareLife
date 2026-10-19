from hashlib import sha256
from uuid import uuid4

from app.application.interfaces.notification import (
    NotificationRepository,
)
from app.domain.entities.notification import Notification
from app.infrastructure.database.connection import get_connection


_NOTIFICATION_COLUMNS = """
id,
user_id,
organization_id,
notification_type,
title,
message,
is_read,
created_at
"""


class PostgresNotificationRepository(NotificationRepository):
    @staticmethod
    def _from_row(row) -> Notification:
        return Notification(
            id=row[0],
            user_id=row[1],
            organization_id=row[2],
            notification_type=row[3],
            title=row[4],
            message=row[5],
            is_read=row[6],
            created_at=row[7],
        )

    @staticmethod
    def _recipient_event_key(
        event_key: str,
        user_id: str,
    ) -> str:
        return sha256(
            f"{event_key}:{user_id}".encode("utf-8")
        ).hexdigest()

    def create_for_users(
        self,
        event_key: str,
        notification_type: str,
        title: str,
        message: str,
        user_ids: list[str],
        organization_id: str | None = None,
    ) -> list[Notification]:
        with get_connection() as connection:
            with connection.transaction():
                return self.create_for_users_in_connection(
                    connection=connection,
                    event_key=event_key,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    user_ids=user_ids,
                    organization_id=organization_id,
                )

    def create_for_users_in_connection(
        self,
        connection,
        event_key: str,
        notification_type: str,
        title: str,
        message: str,
        user_ids: list[str],
        organization_id: str | None = None,
    ) -> list[Notification]:
        """
        Insert notifications using the caller's active transaction.

        This method also lets message persistence and its notification
        succeed or roll back together.
        """
        notifications: list[Notification] = []

        for user_id in sorted(set(user_ids)):
            active_user = connection.execute(
                """
                SELECT 1
                FROM users
                WHERE id = %s
                  AND is_active = TRUE
                """,
                (user_id,),
            ).fetchone()

            if active_user is None:
                continue

            recipient_event_key = self._recipient_event_key(
                event_key,
                user_id,
            )

            row = connection.execute(
                f"""
                INSERT INTO notifications (
                    id,
                    user_id,
                    organization_id,
                    notification_type,
                    title,
                    message,
                    event_key,
                    is_read,
                    created_at
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s,
                    FALSE, CURRENT_TIMESTAMP
                )
                ON CONFLICT (event_key) DO NOTHING
                RETURNING {_NOTIFICATION_COLUMNS}
                """,
                (
                    str(uuid4()),
                    user_id,
                    organization_id,
                    notification_type,
                    title,
                    message,
                    recipient_event_key,
                ),
            ).fetchone()

            # Return the existing notification for a retried event.
            if row is None:
                row = connection.execute(
                    f"""
                    SELECT {_NOTIFICATION_COLUMNS}
                    FROM notifications
                    WHERE event_key = %s
                    """,
                    (recipient_event_key,),
                ).fetchone()

            if row is not None:
                notifications.append(self._from_row(row))

        return notifications

    def list_for_user(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
    ) -> list[Notification]:
        query = f"""
            SELECT {_NOTIFICATION_COLUMNS}
            FROM notifications
            WHERE user_id = %s
        """

        if unread_only:
            query += " AND is_read = FALSE"

        query += """
            ORDER BY created_at DESC, id DESC
            LIMIT %s
        """

        with get_connection() as connection:
            rows = connection.execute(
                query,
                (user_id, limit),
            ).fetchall()

        return [self._from_row(row) for row in rows]

    def mark_as_read(
        self,
        notification_id: str,
        user_id: str,
    ) -> Notification | None:
        with get_connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    f"""
                    UPDATE notifications
                    SET is_read = TRUE
                    WHERE id = %s
                      AND user_id = %s
                    RETURNING {_NOTIFICATION_COLUMNS}
                    """,
                    (notification_id, user_id),
                ).fetchone()

        if row is None:
            return None

        return self._from_row(row)