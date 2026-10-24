from app.application.interfaces.messaging import MessagingRepository
from app.domain.entities.messaging import Conversation, Message
from app.domain.entities.user_context import UserContext


class MessagingService:
    def __init__(self, repository: MessagingRepository):
        self.repository = repository

    def start_conversation(
        self,
        current_user: UserContext,
        recipient_user_id: str,
    ) -> Conversation:
        recipient_user_id = recipient_user_id.strip()

        if not recipient_user_id:
            raise ValueError("A recipient user ID is required.")

        if recipient_user_id == current_user.user_id:
            raise ValueError(
                "You cannot start a conversation with yourself."
            )

        return self.repository.get_or_create_conversation(
            starter_user_id=current_user.user_id,
            recipient_user_id=recipient_user_id,
        )

    def list_conversations(
        self,
        current_user: UserContext,
    ) -> list[Conversation]:
        return self.repository.list_conversations(
            current_user.user_id
        )

    def get_messages(
        self,
        current_user: UserContext,
        conversation_id: str,
    ) -> list[Message]:
        return self.repository.list_messages(
            user_id=current_user.user_id,
            conversation_id=conversation_id,
        )

    def send_message(
        self,
        current_user: UserContext,
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

        return self.repository.send_message(
            user_id=current_user.user_id,
            conversation_id=conversation_id,
            body=body,
        )