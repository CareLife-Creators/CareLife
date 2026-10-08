from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from app.application.schemas.organization import (
    DaycareDirectoryResponse,
    OrganizationVerificationDecisionRequest,
    OrganizationVerificationResponse,
)
from app.application.use_cases.organization_verification import (
    OrganizationVerificationService,
)
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import (
    require_organization_access,
    require_role,
)
from app.presentation.api.dependencies.organization import (
    get_organization_verification_service,
)


router = APIRouter(
    prefix="/organizations",
    tags=["Organization Verification"],
)


@router.get(
    "/daycare",
    response_model=list[DaycareDirectoryResponse],
)
def get_daycare_directory(
    search: str | None = Query(
        default=None,
        max_length=100,
    ),
    location: str | None = Query(
        default=None,
        max_length=100,
    ),
    service: OrganizationVerificationService = Depends(
        get_organization_verification_service
    ),
):
    organizations = service.get_daycare_directory(
        search=search,
        location=location,
    )

    return [
        DaycareDirectoryResponse.from_entity(
            organization
        )
        for organization in organizations
    ]


@router.get(
    "/daycare/{organization_id}",
    response_model=DaycareDirectoryResponse,
)
def get_public_daycare(
    organization_id: str,
    service: OrganizationVerificationService = Depends(
        get_organization_verification_service
    ),
):
    try:
        organization = service.get_public_daycare(
            organization_id
        )

        return DaycareDirectoryResponse.from_entity(
            organization
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/verification/pending",
    response_model=list[OrganizationVerificationResponse],
)
def get_pending_organizations(
    _current_user: UserContext = Depends(
        require_role(Role.CARELIFE_ADMIN)
    ),
    service: OrganizationVerificationService = Depends(
        get_organization_verification_service
    ),
):
    return service.get_pending()


@router.post(
    "/{organization_id}/verification/approve",
    response_model=OrganizationVerificationResponse,
)
def approve_organization(
    organization_id: str,
    current_user: UserContext = Depends(
        require_role(Role.CARELIFE_ADMIN)
    ),
    service: OrganizationVerificationService = Depends(
        get_organization_verification_service
    ),
):
    try:
        return service.approve(
            organization_id,
            current_user.user_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/{organization_id}/verification/reject",
    response_model=OrganizationVerificationResponse,
)
def reject_organization(
    organization_id: str,
    request: OrganizationVerificationDecisionRequest,
    current_user: UserContext = Depends(
        require_role(Role.CARELIFE_ADMIN)
    ),
    service: OrganizationVerificationService = Depends(
        get_organization_verification_service
    ),
):
    try:
        return service.reject(
            organization_id,
            current_user.user_id,
            request.message,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


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
        return service.get_status(
            organization_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc