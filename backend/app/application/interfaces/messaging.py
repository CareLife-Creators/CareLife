from typing import Protocol

from app.domain.entities.messaging import Conversation, Message


class MessagingRepository(Protocol):
    def get_or_create_conversation(
        self,
        starter_user_id: str,
        recipient_user_id: str,
    ) -> Conversation:
        ...

    def list_conversations(
        self,
        user_id: str,
    ) -> list[Conversation]:
        ...

    def list_messages(
        self,
        user_id: str,
        conversation_id: str,
    ) -> list[Message]:
        ...

    def send_message(
        self,
        user_id: str,
        conversation_id: str,
        body: str,
    ) -> Message:
        ...