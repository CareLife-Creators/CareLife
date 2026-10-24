from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.organization import (
    OrganizationApplicantApplicationResponse,
    OrganizationRegistrationRequest,
)
from app.application.use_cases.organization_registration import (
    OrganizationRegistrationService,
)
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import (
    get_current_user,
)
from app.presentation.api.dependencies.organization import (
    get_organization_registration_service,
    get_organization_verification_service,
)
from app.application.use_cases.organization_verification import OrganizationVerificationService


router = APIRouter(
    prefix="/organizations",
    tags=["Organization Registration"],
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register_organization(
    request: OrganizationRegistrationRequest,
    current_user: UserContext = Depends(get_current_user),
    service: OrganizationRegistrationService = Depends(
        get_organization_registration_service
    ),
):
    if current_user.role == Role.CARELIFE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator accounts cannot submit organization applications",
        )

    return service.register(
        request=request,
        submitted_by=current_user.user_id,
    )


@router.get(
    "/applications/mine",
    response_model=list[OrganizationApplicantApplicationResponse],
)
def list_my_organization_applications(
    current_user: UserContext = Depends(get_current_user),
    service: OrganizationVerificationService = Depends(get_organization_verification_service),
):
    return [
        OrganizationApplicantApplicationResponse.from_entity(item)
        for item in service.get_submitted_by(current_user.user_id)
    ]


@router.get("/mine")
def list_my_approved_organizations(
    current_user: UserContext = Depends(get_current_user),
):
    return [
        {"organization_id": organization_id, "organization_role": role}
        for organization_id, role in current_user.organization_roles.items()
    ]
