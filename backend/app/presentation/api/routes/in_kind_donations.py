from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.in_kind_donation import (
    InKindDonationPledgeCreateRequest,
    InKindDonationPledgeResponse,
    InKindDonationStatusUpdateRequest,
)
from app.application.use_cases.in_kind_donations import (
    InKindDonationService,
)
from app.domain.entities.user_context import UserContext
from app.presentation.api.dependencies.authorization import (
    get_current_user,
)
from app.presentation.api.dependencies.in_kind_donation import (
    get_in_kind_donation_service,
)


router = APIRouter(tags=["In-Kind Donations"])


def _raise_http_error(exc: Exception) -> None:
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
    "/donation-needs/{need_id}/in-kind-pledges",
    response_model=InKindDonationPledgeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_in_kind_pledge(
    need_id: str,
    request: InKindDonationPledgeCreateRequest,
    current_user: UserContext = Depends(get_current_user),
    service: InKindDonationService = Depends(
        get_in_kind_donation_service
    ),
):
    try:
        return service.create_pledge(
            current_user,
            need_id,
            request,
        )
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.get(
    "/my/in-kind-pledges",
    response_model=list[InKindDonationPledgeResponse],
)
def list_my_in_kind_pledges(
    current_user: UserContext = Depends(get_current_user),
    service: InKindDonationService = Depends(
        get_in_kind_donation_service
    ),
):
    try:
        return service.list_my_pledges(current_user)
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.get(
    "/organizations/{organization_id}/in-kind-pledges",
    response_model=list[InKindDonationPledgeResponse],
)
def list_organization_in_kind_pledges(
    organization_id: str,
    current_user: UserContext = Depends(get_current_user),
    service: InKindDonationService = Depends(
        get_in_kind_donation_service
    ),
):
    try:
        return service.list_organization_pledges(
            current_user,
            organization_id,
        )
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.patch(
    "/organizations/{organization_id}/in-kind-pledges/{pledge_id}/status",
    response_model=InKindDonationPledgeResponse,
)
def update_in_kind_pledge_status(
    organization_id: str,
    pledge_id: str,
    request: InKindDonationStatusUpdateRequest,
    current_user: UserContext = Depends(get_current_user),
    service: InKindDonationService = Depends(
        get_in_kind_donation_service
    ),
):
    try:
        return service.update_pledge_status(
            current_user,
            organization_id,
            pledge_id,
            request,
        )
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)