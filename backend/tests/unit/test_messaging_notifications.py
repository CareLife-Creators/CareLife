from unittest.mock import Mock

import pytest

from app.application.use_cases.messaging import MessagingService
from app.application.use_cases.notifications import NotificationService
from app.domain.entities.user_context import Role, UserContext
from app.infrastructure.repositories.messaging import (
    PostgresMessagingRepository,
)


def make_user(user_id: str = "user-1") -> UserContext:
    return UserContext(
        user_id=user_id,
        role=Role.PARENT_GUARDIAN,
    )


def test_start_conversation_rejects_self_without_repository_write() -> None:
    repository = Mock()
    service = MessagingService(repository)

    with pytest.raises(ValueError, match="yourself"):
        service.start_conversation(make_user(), "user-1")

    repository.get_or_create_conversation.assert_not_called()


def test_start_conversation_trims_recipient_id() -> None:
    repository = Mock()
    service = MessagingService(repository)
    repository.get_or_create_conversation.return_value = "conversation"

    result = service.start_conversation(make_user(), " recipient-1 ")

    assert result == "conversation"
    repository.get_or_create_conversation.assert_called_once_with(
        starter_user_id="user-1",
        recipient_user_id="recipient-1",
    )


@pytest.mark.parametrize("body", ["", "   ", "x" * 5001])
def test_send_message_rejects_invalid_body(body: str) -> None:
    repository = Mock()
    service = MessagingService(repository)

    with pytest.raises(ValueError):
        service.send_message(make_user(), "conversation-1", body)

    repository.send_message.assert_not_called()


def test_send_message_trims_body_and_uses_authenticated_user() -> None:
    repository = Mock()
    service = MessagingService(repository)
    repository.send_message.return_value = "message"

    result = service.send_message(
        make_user("sender-1"),
        "conversation-1",
        "  Hello  ",
    )

    assert result == "message"
    repository.send_message.assert_called_once_with(
        user_id="sender-1",
        conversation_id="conversation-1",
        body="Hello",
    )


class FakeResult:
    def __init__(self, row):
        self.row = row

    def fetchone(self):
        return self.row


class FakeConnection:
    def __init__(self, row):
        self.execute = Mock(return_value=FakeResult(row))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def transaction(self):
        return self


def test_non_participant_cannot_read_conversation_messages(
    monkeypatch,
) -> None:
    connection = FakeConnection(("participant-1", "participant-2"))
    monkeypatch.setattr(
        "app.infrastructure.repositories.messaging.get_connection",
        lambda: connection,
    )
    repository = PostgresMessagingRepository(
        notification_repository=Mock(),
    )

    with pytest.raises(PermissionError, match="not a participant"):
        repository.list_messages("outsider", "conversation-1")

    # The repository must reject access before querying any message rows.
    connection.execute.assert_called_once()


def test_non_participant_cannot_send_conversation_messages(
    monkeypatch,
) -> None:
    connection = FakeConnection(("participant-1", "participant-2"))
    monkeypatch.setattr(
        "app.infrastructure.repositories.messaging.get_connection",
        lambda: connection,
    )
    repository = PostgresMessagingRepository(
        notification_repository=Mock(),
    )

    with pytest.raises(PermissionError, match="not a participant"):
        repository.send_message(
            "outsider",
            "conversation-1",
            "Unauthorized message",
        )

    # No INSERT or notification creation should happen after access fails.
    connection.execute.assert_called_once()


@pytest.mark.parametrize(
    ("field", "value", "error_text"),
    [
        ("event_key", "  ", "event key"),
        ("notification_type", "  ", "Invalid notification type"),
        ("title", "  ", "Notification title"),
        ("message", "  ", "Notification message"),
    ],
)
def test_notification_creation_rejects_missing_required_values(
    field: str,
    value: str,
    error_text: str,
) -> None:
    repository = Mock()
    service = NotificationService(repository)
    payload = {
        "event_key": "event-1",
        "notification_type": "message_received",
        "title": "A notification",
        "message": "A message",
        "user_ids": ["recipient-1"],
    }
    payload[field] = value

    with pytest.raises(ValueError, match=error_text):
        service.create_for_users(**payload)

    repository.create_for_users.assert_not_called()


def test_notification_creation_deduplicates_recipients_and_normalizes_text() -> None:
    repository = Mock()
    service = NotificationService(repository)
    repository.create_for_users.return_value = []

    result = service.create_for_users(
        event_key=" event-1 ",
        notification_type=" message_received ",
        title=" New message ",
        message=" You received a message. ",
        user_ids=["recipient-1", "recipient-2", "recipient-1"],
    )

    assert result == []
    kwargs = repository.create_for_users.call_args.kwargs
    assert kwargs["event_key"] == "event-1"
    assert kwargs["notification_type"] == "message_received"
    assert kwargs["title"] == "New message"
    assert kwargs["message"] == "You received a message."
    assert set(kwargs["user_ids"]) == {"recipient-1", "recipient-2"}


@pytest.mark.parametrize("limit", [0, 101])
def test_notification_list_rejects_out_of_range_limit(limit: int) -> None:
    repository = Mock()
    service = NotificationService(repository)

    with pytest.raises(ValueError, match="Limit must be between 1 and 100"):
        service.list_for_user("user-1", limit=limit)

    repository.list_for_user.assert_not_called()


def test_notification_list_is_scoped_to_requested_user() -> None:
    repository = Mock()
    service = NotificationService(repository)
    repository.list_for_user.return_value = []

    result = service.list_for_user(
        user_id="user-1",
        unread_only=True,
        limit=25,
    )

    assert result == []
    repository.list_for_user.assert_called_once_with(
        user_id="user-1",
        unread_only=True,
        limit=25,
    )


def test_mark_as_read_reports_missing_or_unowned_notification() -> None:
    repository = Mock()
    service = NotificationService(repository)
    repository.mark_as_read.return_value = None

    with pytest.raises(LookupError, match="Notification not found"):
        service.mark_as_read("notification-1", "user-1")

    repository.mark_as_read.assert_called_once_with(
        notification_id="notification-1",
        user_id="user-1",
    )
