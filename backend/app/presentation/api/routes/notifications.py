from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.schemas.notification import NotificationResponse
from app.application.use_cases.notifications import NotificationService
from app.domain.entities.user_context import UserContext
from app.presentation.api.dependencies.authorization import (
    get_current_user,
)
from app.presentation.api.dependencies.notifications import (
    get_notification_service,
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get(
    "",
    response_model=list[NotificationResponse],
)
def list_my_notifications(
    unread_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: UserContext = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> list[NotificationResponse]:
    return service.list_for_user(
        user_id=current_user.user_id,
        unread_only=unread_only,
        limit=limit,
    )


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_notification_as_read(
    notification_id: str,
    current_user: UserContext = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationResponse:
    try:
        return service.mark_as_read(
            notification_id=notification_id,
            user_id=current_user.user_id,
        )
    except LookupError as exc:
        # A notification owned by someone else is not exposed.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        ) from exc