from fastapi import APIRouter, Depends, HTTPException

from app.application.schemas.login import LoginRequest, LoginResponse
from app.application.use_cases.login import LoginService
from app.presentation.api.dependencies.login import get_login_service


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    service: LoginService = Depends(get_login_service),
):
    try:
        user = service.login(
            email=payload.email,
            password=payload.password,
        )

        return LoginResponse(
            message="Login successful",
            user_id=user.id,
            email=user.email,
            username=user.username,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail=str(exc),
        ) from exc