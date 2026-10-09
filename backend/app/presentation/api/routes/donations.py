from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.schemas.donation import (
    DonationCampaignCreateRequest,
    DonationCampaignResponse,
    DonationCampaignUpdateRequest,
    DonationNeedCreateRequest,
    DonationNeedResponse,
    DonationNeedUpdateRequest,
)
from app.application.use_cases.donations import DonationService
from app.domain.entities.user_context import UserContext
from app.presentation.api.dependencies.authorization import get_current_user
from app.presentation.api.dependencies.donation import get_donation_service


router = APIRouter(tags=["Donation Campaigns and Needs"])


def _raise_http_error(exc: Exception) -> None:
    if isinstance(exc, PermissionError):
        code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, LookupError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ValueError):
        code = status.HTTP_400_BAD_REQUEST
    else:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
    raise HTTPException(status_code=code, detail=str(exc)) from exc


@router.post(
    "/organizations/{organization_id}/donation-campaigns",
    response_model=DonationCampaignResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_campaign(
    organization_id: str,
    request: DonationCampaignCreateRequest,
    current_user: UserContext = Depends(get_current_user),
    service: DonationService = Depends(get_donation_service),
):
    try:
        return service.create_campaign(current_user, organization_id, request)
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.get(
    "/organizations/{organization_id}/donation-campaigns",
    response_model=list[DonationCampaignResponse],
)
def list_organization_campaigns(
    organization_id: str,
    current_user: UserContext = Depends(get_current_user),
    service: DonationService = Depends(get_donation_service),
):
    try:
        return service.list_organization_campaigns(current_user, organization_id)
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.patch(
    "/organizations/{organization_id}/donation-campaigns/{campaign_id}",
    response_model=DonationCampaignResponse,
)
def update_campaign(
    organization_id: str,
    campaign_id: str,
    request: DonationCampaignUpdateRequest,
    current_user: UserContext = Depends(get_current_user),
    service: DonationService = Depends(get_donation_service),
):
    try:
        return service.update_campaign(current_user, organization_id, campaign_id, request)
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.get("/donation-campaigns", response_model=list[DonationCampaignResponse])
def list_public_campaigns(
    organization_id: str | None = Query(default=None, min_length=1),
    service: DonationService = Depends(get_donation_service),
):
    return service.list_public_campaigns(organization_id)


@router.get("/donation-campaigns/{campaign_id}", response_model=DonationCampaignResponse)
def get_public_campaign(
    campaign_id: str,
    service: DonationService = Depends(get_donation_service),
):
    try:
        return service.get_public_campaign(campaign_id)
    except LookupError as exc:
        _raise_http_error(exc)


@router.post(
    "/organizations/{organization_id}/donation-needs",
    response_model=DonationNeedResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_need(
    organization_id: str,
    request: DonationNeedCreateRequest,
    current_user: UserContext = Depends(get_current_user),
    service: DonationService = Depends(get_donation_service),
):
    try:
        return service.create_need(current_user, organization_id, request)
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.get(
    "/organizations/{organization_id}/donation-needs",
    response_model=list[DonationNeedResponse],
)
def list_organization_needs(
    organization_id: str,
    current_user: UserContext = Depends(get_current_user),
    service: DonationService = Depends(get_donation_service),
):
    try:
        return service.list_organization_needs(current_user, organization_id)
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.patch(
    "/organizations/{organization_id}/donation-needs/{need_id}",
    response_model=DonationNeedResponse,
)
def update_need(
    organization_id: str,
    need_id: str,
    request: DonationNeedUpdateRequest,
    current_user: UserContext = Depends(get_current_user),
    service: DonationService = Depends(get_donation_service),
):
    try:
        return service.update_need(current_user, organization_id, need_id, request)
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.get("/donation-needs", response_model=list[DonationNeedResponse])
def list_public_needs(
    organization_id: str | None = Query(default=None, min_length=1),
    service: DonationService = Depends(get_donation_service),
):
    return service.list_public_needs(organization_id)


@router.get("/donation-needs/{need_id}", response_model=DonationNeedResponse)
def get_public_need(
    need_id: str,
    service: DonationService = Depends(get_donation_service),
):
    try:
        return service.get_public_need(need_id)
    except LookupError as exc:
        _raise_http_error(exc)
