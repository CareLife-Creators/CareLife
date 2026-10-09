
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.schemas.caregiver import (
    CaregiverDocumentSubmitRequest,
    CaregiverProfileCreateRequest,
    CaregiverProfileResponse,
    CaregiverProfileUpdateRequest,
    CaregiverPublicProfileResponse,
    CaregiverVerificationDecisionRequest,
)
from app.application.use_cases.caregivers import CaregiverService
from app.domain.entities.caregiver import CaregiverType
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import require_role
from app.presentation.api.dependencies.caregiver import (
    get_caregiver_service,
)


router = APIRouter(
    prefix="/caregivers",
    tags=["Caregiver Profiles and Verification"],
)


@router.post(
    "/me/profile",
    response_model=CaregiverProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_my_profile(
    request: CaregiverProfileCreateRequest,
    current_user: UserContext = Depends(
        require_role(Role.INDEPENDENT_CAREGIVER)
    ),
    service: CaregiverService = Depends(get_caregiver_service),
):
    try:
        profile = service.create_profile(current_user, request)
        return CaregiverProfileResponse.from_entity(profile)
    except PermissionError as exc:
        raise HTTPException(403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, detail=str(exc)) from exc


@router.get(
    "/me/profile",
    response_model=CaregiverProfileResponse,
)
def get_my_profile(
    current_user: UserContext = Depends(
        require_role(Role.INDEPENDENT_CAREGIVER)
    ),
    service: CaregiverService = Depends(get_caregiver_service),
):
    try:
        profile = service.get_my_profile(current_user)
        return CaregiverProfileResponse.from_entity(profile)
    except PermissionError as exc:
        raise HTTPException(403, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, detail=str(exc)) from exc


@router.patch(
    "/me/profile",
    response_model=CaregiverProfileResponse,
)
def update_my_profile(
    request: CaregiverProfileUpdateRequest,
    current_user: UserContext = Depends(
        require_role(Role.INDEPENDENT_CAREGIVER)
    ),
    service: CaregiverService = Depends(get_caregiver_service),
):
    try:
        profile = service.update_profile(current_user, request)
        return CaregiverProfileResponse.from_entity(profile)
    except PermissionError as exc:
        raise HTTPException(403, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, detail=str(exc)) from exc


@router.post(
    "/me/profile/documents",
    response_model=CaregiverProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_my_document(
    request: CaregiverDocumentSubmitRequest,
    current_user: UserContext = Depends(
        require_role(Role.INDEPENDENT_CAREGIVER)
    ),
    service: CaregiverService = Depends(get_caregiver_service),
):
    try:
        profile = service.submit_document(current_user, request)
        return CaregiverProfileResponse.from_entity(profile)
    except PermissionError as exc:
        raise HTTPException(403, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, detail=str(exc)) from exc


@router.get(
    "/verification/pending",
    response_model=list[CaregiverProfileResponse],
)
def list_pending_caregivers(
    current_user: UserContext = Depends(
        require_role(Role.CARELIFE_ADMIN)
    ),
    service: CaregiverService = Depends(get_caregiver_service),
):
    profiles = service.list_pending_profiles(current_user)

    return [
        CaregiverProfileResponse.from_entity(profile)
        for profile in profiles
    ]


@router.post(
    "/{caregiver_id}/verification",
    response_model=CaregiverProfileResponse,
)
def review_caregiver(
    caregiver_id: str,
    request: CaregiverVerificationDecisionRequest,
    current_user: UserContext = Depends(
        require_role(Role.CARELIFE_ADMIN)
    ),
    service: CaregiverService = Depends(get_caregiver_service),
):
    try:
        profile = service.review_profile(
            current_user,
            caregiver_id,
            request,
        )
        return CaregiverProfileResponse.from_entity(profile)
    except PermissionError as exc:
        raise HTTPException(403, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, detail=str(exc)) from exc


@router.get(
    "",
    response_model=list[CaregiverPublicProfileResponse],
)
def list_public_caregivers(
    search: str | None = Query(default=None, max_length=100),
    location: str | None = Query(default=None, max_length=100),
    service_type: CaregiverType | None = Query(default=None),
    service: CaregiverService = Depends(get_caregiver_service),
):
    profiles = service.list_public_profiles(
        search=search,
        location=location,
        service_type=service_type,
    )

    return [
        CaregiverPublicProfileResponse.from_entity(profile)
        for profile in profiles
    ]


@router.get(
    "/{caregiver_id}",
    response_model=CaregiverPublicProfileResponse,
)
def get_public_caregiver(
    caregiver_id: str,
    service: CaregiverService = Depends(get_caregiver_service),
):
    try:
        profile = service.get_public_profile(caregiver_id)
        return CaregiverPublicProfileResponse.from_entity(profile)
    except LookupError as exc:
        raise HTTPException(404, detail=str(exc)) from exc