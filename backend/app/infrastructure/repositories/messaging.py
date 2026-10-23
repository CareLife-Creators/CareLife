from uuid import uuid4

from app.application.interfaces.messaging import MessagingRepository
from app.domain.entities.messaging import Conversation, Message
from app.infrastructure.database.connection import get_connection
from app.infrastructure.repositories.notifications import (
    PostgresNotificationRepository,
)


class PostgresMessagingRepository(MessagingRepository):
    def __init__(
        self,
        notification_repository: (
            PostgresNotificationRepository | None
        ) = None,
    ):
        self.notification_repository = (
            notification_repository
            or PostgresNotificationRepository()
        )

    @staticmethod
    def _conversation_from_row(row) -> Conversation:
        return Conversation(
            id=row[0],
            participant_one_id=row[1],
            participant_two_id=row[2],
            created_at=row[3],
            last_message_at=row[4],
            other_user_name=row[5] if len(row) > 5 else None,
            other_user_role=row[6] if len(row) > 6 else None,
        )

    @staticmethod
    def _message_from_row(row) -> Message:
        return Message(
            id=row[0],
            conversation_id=row[1],
            sender_user_id=row[2],
            body=row[3],
            created_at=row[4],
        )

    @staticmethod
    def _assert_participant(
        participant_one_id: str,
        participant_two_id: str,
        user_id: str,
    ) -> None:
        if user_id not in {
            participant_one_id,
            participant_two_id,
        }:
            raise PermissionError(
                "You are not a participant in this conversation."
            )

    def get_or_create_conversation(
        self,
        starter_user_id: str,
        recipient_user_id: str,
    ) -> Conversation:
        if starter_user_id == recipient_user_id:
            raise ValueError(
                "You cannot start a conversation with yourself."
            )

        participant_one_id, participant_two_id = sorted(
            (starter_user_id, recipient_user_id)
        )

        with get_connection() as connection:
            with connection.transaction():
                active_users = connection.execute(
                    """
                    SELECT id
                    FROM users
                    WHERE id IN (%s, %s)
                      AND is_active = TRUE
                    ORDER BY id
                    FOR SHARE
                    """,
                    (
                        participant_one_id,
                        participant_two_id,
                    ),
                ).fetchall()

                if len(active_users) != 2:
                    raise LookupError(
                        "Recipient user not found or inactive."
                    )

                connection.execute(
                    """
                    INSERT INTO conversations (
                        id,
                        participant_one_id,
                        participant_two_id,
                        created_at
                    )
                    VALUES (
                        %s, %s, %s, CURRENT_TIMESTAMP
                    )
                    ON CONFLICT (
                        participant_one_id,
                        participant_two_id
                    ) DO NOTHING
                    """,
                    (
                        str(uuid4()),
                        participant_one_id,
                        participant_two_id,
                    ),
                )

                row = connection.execute(
                    """
                    SELECT
                        id,
                        participant_one_id,
                        participant_two_id,
                        created_at,
                        last_message_at
                    FROM conversations
                    WHERE participant_one_id = %s
                      AND participant_two_id = %s
                    """,
                    (
                        participant_one_id,
                        participant_two_id,
                    ),
                ).fetchone()

        if row is None:
            raise RuntimeError(
                "Conversation could not be loaded after creation."
            )

        return self._conversation_from_row(row)

    def list_conversations(
        self,
        user_id: str,
    ) -> list[Conversation]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    c.id,
                    c.participant_one_id,
                    c.participant_two_id,
                    c.created_at,
                    c.last_message_at,
                    other_user.full_name,
                    other_role.name
                FROM conversations c
                JOIN users other_user
                  ON other_user.id = CASE
                    WHEN c.participant_one_id = %s THEN c.participant_two_id
                    ELSE c.participant_one_id
                  END
                LEFT JOIN roles other_role ON other_role.id = other_user.role_id
                WHERE c.participant_one_id = %s
                   OR c.participant_two_id = %s
                ORDER BY
                    COALESCE(c.last_message_at, c.created_at) DESC,
                    c.id DESC
                """,
                (user_id, user_id, user_id),
            ).fetchall()

        return [
            self._conversation_from_row(row)
            for row in rows
        ]

    def list_messages(
        self,
        user_id: str,
        conversation_id: str,
    ) -> list[Message]:
        with get_connection() as connection:
            conversation = connection.execute(
                """
                SELECT participant_one_id, participant_two_id
                FROM conversations
                WHERE id = %s
                """,
                (conversation_id,),
            ).fetchone()

            if conversation is None:
                raise LookupError("Conversation not found.")

            self._assert_participant(
                participant_one_id=conversation[0],
                participant_two_id=conversation[1],
                user_id=user_id,
            )

            rows = connection.execute(
                """
                SELECT
                    id,
                    conversation_id,
                    sender_user_id,
                    body,
                    created_at
                FROM messages
                WHERE conversation_id = %s
                ORDER BY created_at ASC, id ASC
                """,
                (conversation_id,),
            ).fetchall()

        return [
            self._message_from_row(row)
            for row in rows
        ]

    def send_message(
        self,
        user_id: str,
        conversation_id: str,
        body: str,
    ) -> Message:
        body = body.strip()

        if not body:
            raise ValueError("Message content cannot be empty.")

        if len(body) > 5000:
            raise ValueError(
                "Message content cannot exceed 5000 characters."
            )

        with get_connection() as connection:
            with connection.transaction():
                conversation = connection.execute(
                    """
                    SELECT participant_one_id, participant_two_id
                    FROM conversations
                    WHERE id = %s
                    FOR UPDATE
                    """,
                    (conversation_id,),
                ).fetchone()

                if conversation is None:
                    raise LookupError("Conversation not found.")

                participant_one_id = conversation[0]
                participant_two_id = conversation[1]

                self._assert_participant(
                    participant_one_id=participant_one_id,
                    participant_two_id=participant_two_id,
                    user_id=user_id,
                )

                recipient_user_id = (
                    participant_two_id
                    if user_id == participant_one_id
                    else participant_one_id
                )

                row = connection.execute(
                    """
                    INSERT INTO messages (
                        id,
                        conversation_id,
                        sender_user_id,
                        body,
                        created_at
                    )
                    VALUES (
                        %s, %s, %s, %s, CURRENT_TIMESTAMP
                    )
                    RETURNING
                        id,
                        conversation_id,
                        sender_user_id,
                        body,
                        created_at
                    """,
                    (
                        str(uuid4()),
                        conversation_id,
                        user_id,
                        body,
                    ),
                ).fetchone()

                connection.execute(
                    """
                    UPDATE conversations
                    SET last_message_at = %s
                    WHERE id = %s
                    """,
                    (row[4], conversation_id),
                )

                # The message and its recipient notification share
                # one transaction.
                self.notification_repository.create_for_users_in_connection(
                    connection=connection,
                    event_key=f"message:{row[0]}",
                    notification_type="message_received",
                    title="New CareLife message",
                    message="You received a new message in CareLife.",
                    user_ids=[recipient_user_id],
                )

        return self._message_from_row(row)
