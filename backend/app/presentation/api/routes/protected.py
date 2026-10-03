from fastapi import APIRouter, Depends

from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import require_role
from app.presentation.api.dependencies.authorization import (
    require_organization_access,
    require_role,
)
from app.presentation.api.dependencies.authorization import get_current_user

router = APIRouter(
    prefix="/protected",
    tags=["Authorization"],
)


@router.get("/admin")
def admin_only(
    current_user: UserContext = Depends(
        require_role(Role.CARELIFE_ADMIN)
    ),
):
    return {
        "message": "Authorized access",
        "user_id": current_user.user_id,
        "role": current_user.role,
    }

@router.get("/organizations/{organization_id}")
def organization_only(
    organization_id: str,
    current_user: UserContext = Depends(require_organization_access),
):
    return {
        "message": "Organization access granted",
        "user_id": current_user.user_id,
        "organization_id": current_user.organization_id,
    }

@router.get("/me")
def current_user(
    current_user: UserContext = Depends(get_current_user),
):
    return {
        "message": "Authenticated",
        "user_id": current_user.user_id,
    }