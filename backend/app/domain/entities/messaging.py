from datetime import datetime

from pydantic import BaseModel


class Conversation(BaseModel):
    id: str
    participant_one_id: str
    participant_two_id: str
    created_at: datetime
    last_message_at: datetime | None = None


class Message(BaseModel):
    id: str
    conversation_id: str
    sender_user_id: str
    body: str
    created_at: datetime