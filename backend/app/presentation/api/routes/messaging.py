from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.application.schemas.messaging import (
    ConversationCreateRequest,
    ConversationResponse,
    MessageCreateRequest,
    MessageResponse,
)
from app.application.use_cases.messaging import MessagingService
from app.domain.entities.user_context import UserContext
from app.presentation.api.dependencies.authorization import (
    get_current_user,
)
from app.presentation.api.dependencies.messaging import (
    get_messaging_service,
)


router = APIRouter(
    prefix="/messages",
    tags=["Messaging"],
)


def _raise_http_error(exc: Exception) -> None:
    if isinstance(exc, PermissionError):
        code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, LookupError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ValueError):
        code = status.HTTP_400_BAD_REQUEST
    else:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR

    raise HTTPException(
        status_code=code,
        detail=str(exc),
    ) from exc


@router.post(
    "/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_conversation(
    request: ConversationCreateRequest,
    current_user: UserContext = Depends(get_current_user),
    service: MessagingService = Depends(get_messaging_service),
) -> ConversationResponse:
    try:
        return service.start_conversation(
            current_user=current_user,
            recipient_user_id=request.recipient_user_id,
        )
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.get(
    "/conversations",
    response_model=list[ConversationResponse],
)
def list_my_conversations(
    current_user: UserContext = Depends(get_current_user),
    service: MessagingService = Depends(get_messaging_service),
) -> list[ConversationResponse]:
    return service.list_conversations(current_user)


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def get_conversation_messages(
    conversation_id: str,
    current_user: UserContext = Depends(get_current_user),
    service: MessagingService = Depends(get_messaging_service),
) -> list[MessageResponse]:
    try:
        return service.get_messages(
            current_user=current_user,
            conversation_id=conversation_id,
        )
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_conversation_message(
    conversation_id: str,
    request: MessageCreateRequest,
    current_user: UserContext = Depends(get_current_user),
    service: MessagingService = Depends(get_messaging_service),
) -> MessageResponse:
    try:
        return service.send_message(
            current_user=current_user,
            conversation_id=conversation_id,
            body=request.body,
        )
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)