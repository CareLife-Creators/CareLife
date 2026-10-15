from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.user_profile import (
    UserProfileResponse,
    UserProfileUpdateRequest,
)
from app.application.use_cases.user_profile import UserProfileService
from app.domain.entities.user import User
from app.domain.entities.user_context import UserContext
from app.presentation.api.dependencies.authorization import (
    get_current_user,
)
from app.presentation.api.dependencies.user_profile import (
    get_user_profile_service,
)


router = APIRouter(
    prefix="/users/me/profile",
    tags=["User Profile"],
)


def to_profile_response(user: User) -> UserProfileResponse:
    return UserProfileResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role_name,
    )


@router.get(
    "",
    response_model=UserProfileResponse,
)
def get_my_profile(
    current_user: UserContext = Depends(get_current_user),
    service: UserProfileService = Depends(
        get_user_profile_service
    ),
) -> UserProfileResponse:
    try:
        user = service.get_profile(current_user.user_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        ) from exc

    return to_profile_response(user)


@router.patch(
    "",
    response_model=UserProfileResponse,
)
def update_my_profile(
    request: UserProfileUpdateRequest,
    current_user: UserContext = Depends(get_current_user),
    service: UserProfileService = Depends(
        get_user_profile_service
    ),
) -> UserProfileResponse:
    try:
        user = service.update_profile(
            current_user.user_id,
            request.model_dump(exclude_unset=True),
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return to_profile_response(user)