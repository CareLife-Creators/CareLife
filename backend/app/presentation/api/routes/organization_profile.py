from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.organization_profile import (
    OrganizationProfileResponse,
    OrganizationProfileUpdateRequest,
    PublicOrganizationProfileResponse,
    PublicOrphanageProfileResponse,
)
from app.application.use_cases.organization_profile import (
    OrganizationProfileService,
)
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import (
    require_organization_access,
)
from app.presentation.api.dependencies.organization_profile import (
    get_organization_profile_service,
)


router = APIRouter(
    prefix="/organizations",
    tags=["Organization Profile"],
)

orphanage_public_router = APIRouter(
    prefix="/orphanages",
    tags=["Orphanage Public Profile"],
)


STAFF_ORGANIZATION_TYPES = {
    Role.DAYCARE_STAFF: "daycare",
    Role.ORPHANAGE_STAFF: "orphanage",
    Role.CARE_HOME_STAFF: "elderly_care",
}


def get_expected_organization_type(
    current_user: UserContext,
) -> str:
    organization_type = STAFF_ORGANIZATION_TYPES.get(
        current_user.role
    )

    if organization_type is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization staff can manage profiles.",
        )

    return organization_type


@router.get(
    "/{organization_id}/profile",
    response_model=OrganizationProfileResponse,
)
def get_organization_profile(
    organization_id: str,
    current_user: UserContext = Depends(
        require_organization_access
    ),
    service: OrganizationProfileService = Depends(
        get_organization_profile_service
    ),
) -> OrganizationProfileResponse:
    expected_type = get_expected_organization_type(
        current_user
    )

    try:
        profile = service.get_staff_profile(
            organization_id=organization_id,
            expected_organization_type=expected_type,
        )

        return OrganizationProfileResponse.from_entity(
            profile
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization profile not found.",
        ) from exc

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{organization_id}/profile",
    response_model=OrganizationProfileResponse,
)
def update_organization_profile(
    organization_id: str,
    request: OrganizationProfileUpdateRequest,
    current_user: UserContext = Depends(
        require_organization_access
    ),
    service: OrganizationProfileService = Depends(
        get_organization_profile_service
    ),
) -> OrganizationProfileResponse:
    expected_type = get_expected_organization_type(
        current_user
    )

    try:
        profile = service.update_profile(
            organization_id=organization_id,
            changes=request.model_dump(
                exclude_unset=True
            ),
            updated_by=current_user.user_id,
            expected_organization_type=expected_type,
        )

        return OrganizationProfileResponse.from_entity(
            profile
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization profile not found.",
        ) from exc

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get(
    "/{organization_id}/public-profile",
    response_model=PublicOrganizationProfileResponse,
)
def get_public_organization_profile(
    organization_id: str,
    service: OrganizationProfileService = Depends(
        get_organization_profile_service
    ),
) -> PublicOrganizationProfileResponse:
    try:
        profile = service.get_public_profile(
            organization_id
        )

        return PublicOrganizationProfileResponse.from_entity(
            profile
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public organization profile not found.",
        ) from exc


@orphanage_public_router.get(
    "/{organization_id}/public-profile",
    response_model=PublicOrphanageProfileResponse,
)
def get_public_orphanage_profile(
    organization_id: str,
    service: OrganizationProfileService = Depends(
        get_organization_profile_service
    ),
) -> PublicOrphanageProfileResponse:
    """
    Return the public profile for an eligible orphanage.

    No authentication is required because this endpoint is public.
    Only organizations with verified status, a current license,
    and organization type 'orphanage' can be returned.
    """
    try:
        profile = service.get_public_orphanage_profile(
            organization_id
        )

        return PublicOrphanageProfileResponse.from_entity(
            profile
        )

    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public orphanage profile not found.",
        ) from exc