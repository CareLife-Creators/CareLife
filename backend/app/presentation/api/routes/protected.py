from fastapi import APIRouter, Depends

from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import require_role


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