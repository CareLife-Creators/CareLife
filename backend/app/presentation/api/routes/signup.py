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
) -> SignupResponse:
    try:
        service.signup(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            phone=request.phone,
            role=request.role,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    # The response is identical for a new or previously registered email.
    return SignupResponse(message="Signup request received.")
