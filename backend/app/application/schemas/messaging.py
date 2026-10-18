from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class ConversationCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recipient_user_id: str = Field(
        min_length=1,
        max_length=128,
    )

    @field_validator("recipient_user_id")
    @classmethod
    def clean_recipient_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("A recipient user ID is required.")
        return value


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    participant_one_id: str
    participant_two_id: str
    created_at: datetime
    last_message_at: datetime | None = None


class MessageCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    body: str = Field(
        min_length=1,
        max_length=5000,
    )

    @field_validator("body")
    @classmethod
    def clean_body(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message content cannot be empty.")
        return value


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    sender_user_id: str
    body: str
    created_at: datetime