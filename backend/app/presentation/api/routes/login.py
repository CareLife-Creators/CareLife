from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.login import LoginRequest, LoginResponse
from app.application.use_cases.login import LoginService
from app.presentation.api.dependencies.login import get_login_service


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    service: LoginService = Depends(get_login_service),
) -> LoginResponse:
    try:
        access_token = service.login(
            email=str(request.email),
            password=request.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return LoginResponse(access_token=access_token)
