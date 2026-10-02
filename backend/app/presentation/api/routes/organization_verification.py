from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.organization_verification import (
    OrganizationVerificationResponse,
)
from app.application.use_cases.organization_verification import (
    OrganizationVerificationService,
)
from app.presentation.api.dependencies.authorization import (
    require_organization_access,
)
from app.presentation.api.dependencies.organization_verification import (
    get_organization_verification_service,
)
from app.domain.entities.user_context import UserContext


router = APIRouter(
    prefix="/organizations",
    tags=["Organization Verification"],
)


@router.get(
    "/{organization_id}/verification-status",
    response_model=OrganizationVerificationResponse,
)
def get_verification_status(
    organization_id: str,
    _current_user: UserContext = Depends(
        require_organization_access
    ),
    service: OrganizationVerificationService = Depends(
        get_organization_verification_service
    ),
):
    try:
        return service.get_status(organization_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc