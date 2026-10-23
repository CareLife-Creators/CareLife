from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.application.use_cases.user_profile import UserProfileService
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import require_role
from app.presentation.api.dependencies.user_profile import get_user_profile_service


router = APIRouter(prefix="/admin/users", tags=["Administration"])


class AdminUserSummary(BaseModel):
    user_id: str
    email: str
    full_name: str | None = None
    role: str
    is_active: bool
    created_at: datetime
    organization_ids: list[str]


class CreateAdminRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class AccountStatusRequest(BaseModel):
    is_active: bool


class AdminUserCreated(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str
    is_active: bool


@router.get("")
def list_users_for_admin(
    _admin: UserContext = Depends(require_role(Role.CARELIFE_ADMIN)),
    service: UserProfileService = Depends(get_user_profile_service),
) -> list[AdminUserSummary]:
    return service.list_users()

@router.post("", response_model=AdminUserCreated, status_code=status.HTTP_201_CREATED)
def create_admin_account(
    request: CreateAdminRequest,
    admin: UserContext = Depends(require_role(Role.CARELIFE_ADMIN)),
    service: UserProfileService = Depends(get_user_profile_service),
):
    try:
        user = service.create_admin(request.email, request.full_name, request.password, admin.user_id)
        return AdminUserCreated(user_id=user.id, email=user.email, full_name=user.full_name or "", role=user.role_name, is_active=True)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@router.patch("/{user_id}/status", status_code=status.HTTP_204_NO_CONTENT)
def update_account_status(
    user_id: str,
    request: AccountStatusRequest,
    admin: UserContext = Depends(require_role(Role.CARELIFE_ADMIN)),
    service: UserProfileService = Depends(get_user_profile_service),
):
    try:
        if not service.set_user_active(user_id, request.is_active, admin.user_id):
            raise HTTPException(status_code=404, detail="Account not found.")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
