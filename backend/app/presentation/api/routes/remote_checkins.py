from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.remote_checkin import (
    ConsentUpdateRequest,
    RemoteCheckInCreateRequest,
    RemoteCheckInResponse,
    ResidentConsentResponse,
)
from app.application.use_cases.remote_checkins import (
    RemoteCheckInService,
)
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import (
    require_role,
)
from app.presentation.api.dependencies.remote_checkin import (
    get_remote_checkin_service,
)


router = APIRouter(
    prefix="/elder-care",
    tags=["Elder-Care Remote Check-In"],
)


def raise_http_error(exc: Exception) -> None:
    if isinstance(exc, PermissionError):
        code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, LookupError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ValueError):
        code = status.HTTP_400_BAD_REQUEST
    else:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR

    raise HTTPException(
        status_code=code,
        detail=str(exc),
    ) from exc


@router.post(
    "/organizations/{organization_id}/residents/{resident_id}/consent",
    response_model=ResidentConsentResponse,
)
def set_resident_consent(
    organization_id: str,
    resident_id: str,
    request: ConsentUpdateRequest,
    current_user: UserContext = Depends(
        require_role(
            Role.CARE_HOME_STAFF,
            Role.CARELIFE_ADMIN,
        )
    ),
    service: RemoteCheckInService = Depends(
        get_remote_checkin_service
    ),
):
    try:
        consent = service.set_consent(
            user=current_user,
            organization_id=organization_id,
            resident_id=resident_id,
            request=request,
        )
        return ResidentConsentResponse.from_entity(consent)

    except (PermissionError, LookupError, ValueError) as exc:
        raise_http_error(exc)


@router.post(
    "/residents/{resident_id}/check-ins",
    response_model=RemoteCheckInResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_remote_checkin(
    resident_id: str,
    request: RemoteCheckInCreateRequest,
    current_user: UserContext = Depends(
        require_role(Role.FAMILY_REPRESENTATIVE)
    ),
    service: RemoteCheckInService = Depends(
        get_remote_checkin_service
    ),
):
    try:
        checkin = service.create_checkin(
            user=current_user,
            resident_id=resident_id,
            request=request,
        )
        return RemoteCheckInResponse.from_entity(checkin)

    except (PermissionError, LookupError, ValueError) as exc:
        raise_http_error(exc)


@router.get(
    "/residents/{resident_id}/check-ins",
    response_model=list[RemoteCheckInResponse],
)
def list_remote_checkins(
    resident_id: str,
    current_user: UserContext = Depends(
        require_role(
            Role.FAMILY_REPRESENTATIVE,
            Role.CARE_HOME_STAFF,
            Role.CARELIFE_ADMIN,
        )
    ),
    service: RemoteCheckInService = Depends(
        get_remote_checkin_service
    ),
):
    try:
        checkins = service.list_checkins(
            user=current_user,
            resident_id=resident_id,
        )

        return [
            RemoteCheckInResponse.from_entity(checkin)
            for checkin in checkins
        ]

    except (PermissionError, LookupError, ValueError) as exc:
        raise_http_error(exc)