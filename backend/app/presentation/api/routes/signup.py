from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.signup import SignupRequest, SignupResponse
from app.application.use_cases.signup import SignupService
from app.presentation.api.dependencies.signup import get_signup_service


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(
    request: SignupRequest,
    service: SignupService = Depends(get_signup_service),
):
    try:
        user = service.signup(
            username=request.username,
            email=request.email,
            date_of_birth=request.date_of_birth,
            gender=request.gender,
            password=request.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return SignupResponse(
        message="Account created successfully.",
        user_id=user.id,
    )