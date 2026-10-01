from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.password_reset import (
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    PasswordResetResponse,
)
from app.application.use_cases.password_reset import PasswordResetService
from app.presentation.api.dependencies.password_reset import (
    get_password_reset_service,
)


router = APIRouter(
    prefix="/auth/password-reset",
    tags=["Password Reset"],
)


@router.post(
    "/request",
    response_model=PasswordResetResponse,
)
def request_password_reset(
    request: PasswordResetRequest,
    service: PasswordResetService = Depends(
        get_password_reset_service
    ),
):
    message = service.request_reset(request.email)

    return PasswordResetResponse(message=message)


@router.post(
    "/confirm",
    response_model=PasswordResetResponse,
)
def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    service: PasswordResetService = Depends(
        get_password_reset_service
    ),
):
    try:
        message = service.reset_password(
            token=request.token,
            new_password=request.new_password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return PasswordResetResponse(message=message)