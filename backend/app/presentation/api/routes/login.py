from fastapi import APIRouter, Depends, HTTPException

from app.application.schemas.login import (
    LoginRequest,
    LoginResponse,
)
from app.application.use_cases.login import LoginService
from app.application.use_cases.logout import LogoutService
from app.core.security import create_access_token
from app.presentation.api.dependencies.authentication import (
    get_bearer_token,
)
from app.presentation.api.dependencies.login import (
    get_login_service,
)
from app.presentation.api.dependencies.logout import (
    get_logout_service,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    payload: LoginRequest,
    service: LoginService = Depends(get_login_service),
):
    try:
        user = service.login(
            email=payload.email,
            password=payload.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc

    return LoginResponse(
        message="Login successful",
        user_id=user.id,
        email=user.email,
        access_token=create_access_token(user.id),
        token_type="bearer",
    )


@router.post("/logout")
def logout(
    token: str = Depends(get_bearer_token),
    service: LogoutService = Depends(get_logout_service),
):
    try:
        service.logout(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc

    return {"message": "Logout successful"}