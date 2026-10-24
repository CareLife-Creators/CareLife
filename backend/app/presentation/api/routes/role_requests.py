from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.schemas.role_request import (
    RoleRequestCreateRequest,
    RoleRequestResponse,
)
from app.application.use_cases.role_requests import RoleRequestService
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import (
    get_current_user,
    require_role,
)
from app.presentation.api.dependencies.role_requests import (
    get_role_request_service,
)


router = APIRouter(tags=["Role Requests"])


@router.post(
    "/users/me/role-requests",
    response_model=RoleRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_my_role_request(
    request: RoleRequestCreateRequest,
    current_user: UserContext = Depends(get_current_user),
    service: RoleRequestService = Depends(get_role_request_service),
) -> RoleRequestResponse:
    try:
        return service.create(
            user_id=current_user.user_id,
            requested_role=request.requested_role,
            note=request.note,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/users/me/role-requests",
    response_model=list[RoleRequestResponse],
)
def list_my_role_requests(
    current_user: UserContext = Depends(get_current_user),
    service: RoleRequestService = Depends(get_role_request_service),
) -> list[RoleRequestResponse]:
    return service.list_for_user(current_user.user_id)


@router.get(
    "/admin/role-requests",
    response_model=list[RoleRequestResponse],
)
def list_role_requests_for_admin(
    request_status: Literal["pending", "approved", "rejected"] = Query(
        default="pending",
        alias="status",
    ),
    _admin: UserContext = Depends(require_role(Role.CARELIFE_ADMIN)),
    service: RoleRequestService = Depends(get_role_request_service),
) -> list[RoleRequestResponse]:
    return service.list_by_status(request_status)


@router.post(
    "/admin/role-requests/{request_id}/approve",
    response_model=RoleRequestResponse,
)
def approve_role_request(
    request_id: str,
    admin: UserContext = Depends(require_role(Role.CARELIFE_ADMIN)),
    service: RoleRequestService = Depends(get_role_request_service),
) -> RoleRequestResponse:
    try:
        request = service.approve(
            request_id=request_id,
            reviewer_id=admin.user_id,
            reviewer_role=admin.role.value,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role request not found.",
        )
    return request


@router.post(
    "/admin/role-requests/{request_id}/reject",
    response_model=RoleRequestResponse,
)
def reject_role_request(
    request_id: str,
    admin: UserContext = Depends(require_role(Role.CARELIFE_ADMIN)),
    service: RoleRequestService = Depends(get_role_request_service),
) -> RoleRequestResponse:
    try:
        request = service.reject(
            request_id=request_id,
            reviewer_id=admin.user_id,
            reviewer_role=admin.role.value,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role request not found.",
        )
    return request
