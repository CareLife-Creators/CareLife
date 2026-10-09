from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.organization import (
    OrganizationRegistrationRequest,
)
from app.application.use_cases.organization_registration import (
    OrganizationRegistrationService,
)
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import (
    require_role,
)
from app.presentation.api.dependencies.organization import (
    get_organization_registration_service,
)


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
    current_user: UserContext = Depends(
        require_role(
            Role.DAYCARE_STAFF,
            Role.ORPHANAGE_STAFF,
            Role.CARE_HOME_STAFF,
        )
    ),
    service: OrganizationRegistrationService = Depends(
        get_organization_registration_service
    ),
):
    expected_type = {
        Role.DAYCARE_STAFF: "daycare",
        Role.ORPHANAGE_STAFF: "orphanage",
        Role.CARE_HOME_STAFF: "elderly_care",
    }[current_user.role]

    if request.organization_type != expected_type:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your staff role cannot register this organization type",
        )

    return service.register(
        request=request,
        submitted_by=current_user.user_id,
    )