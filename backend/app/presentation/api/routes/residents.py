from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.schemas.resident import (
    ResidentProfileCreateRequest,
    ResidentProfileResponse,
    ResidentProfileUpdateRequest,
)
from app.application.use_cases.residents import (
    ResidentProfileService,
)
from app.domain.entities.resident import ResidentProfileStatus
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import (
    require_role,
)
from app.presentation.api.dependencies.resident import (
    get_resident_profile_service,
)


router = APIRouter(
    prefix="/elder-care",
    tags=["Elder-Care Resident Profiles"],
)


def _raise_http_error(exc: Exception) -> None:
    if isinstance(exc, PermissionError):
        code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, LookupError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ValueError):
        code = status.HTTP_422_UNPROCESSABLE_ENTITY
    else:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR

    raise HTTPException(
        status_code=code,
        detail=str(exc),
    ) from exc


@router.post(
    "/organizations/{organization_id}/residents",
    response_model=ResidentProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_resident_profile(
    organization_id: str,
    request: ResidentProfileCreateRequest,
    current_user: UserContext = Depends(
        require_role(
            Role.CARE_HOME_STAFF,
            Role.CARELIFE_ADMIN,
        )
    ),
    service: ResidentProfileService = Depends(
        get_resident_profile_service
    ),
) -> ResidentProfileResponse:
    try:
        profile = service.create_profile(
            user=current_user,
            organization_id=organization_id,
            request=request,
        )

        return ResidentProfileResponse.from_entity(profile)

    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.get(
    "/organizations/{organization_id}/residents",
    response_model=list[ResidentProfileResponse],
)
def list_resident_profiles(
    organization_id: str,
    profile_status: ResidentProfileStatus | None = Query(
        default=None,
        alias="status",
    ),
    current_user: UserContext = Depends(
        require_role(
            Role.CARE_HOME_STAFF,
            Role.CARELIFE_ADMIN,
        )
    ),
    service: ResidentProfileService = Depends(
        get_resident_profile_service
    ),
) -> list[ResidentProfileResponse]:
    try:
        profiles = service.list_profiles(
            user=current_user,
            organization_id=organization_id,
            profile_status=profile_status,
        )

        return [
            ResidentProfileResponse.from_entity(profile)
            for profile in profiles
        ]

    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.get(
    "/organizations/{organization_id}/residents/{resident_id}",
    response_model=ResidentProfileResponse,
)
def get_resident_profile(
    organization_id: str,
    resident_id: str,
    current_user: UserContext = Depends(
        require_role(
            Role.CARE_HOME_STAFF,
            Role.CARELIFE_ADMIN,
        )
    ),
    service: ResidentProfileService = Depends(
        get_resident_profile_service
    ),
) -> ResidentProfileResponse:
    try:
        profile = service.get_profile(
            user=current_user,
            organization_id=organization_id,
            resident_id=resident_id,
        )

        return ResidentProfileResponse.from_entity(profile)

    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.patch(
    "/organizations/{organization_id}/residents/{resident_id}",
    response_model=ResidentProfileResponse,
)
def update_resident_profile(
    organization_id: str,
    resident_id: str,
    request: ResidentProfileUpdateRequest,
    current_user: UserContext = Depends(
        require_role(
            Role.CARE_HOME_STAFF,
            Role.CARELIFE_ADMIN,
        )
    ),
    service: ResidentProfileService = Depends(
        get_resident_profile_service
    ),
) -> ResidentProfileResponse:
    try:
        profile = service.update_profile(
            user=current_user,
            organization_id=organization_id,
            resident_id=resident_id,
            changes=request.model_dump(
                exclude_unset=True
            ),
        )

        return ResidentProfileResponse.from_entity(profile)

    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)