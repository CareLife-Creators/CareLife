from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status

from app.domain.entities.user_context import Role, UserContext


def get_current_user(request: Request) -> UserContext:
    user = getattr(request.state, "user", None)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    return user


def require_role(*allowed_roles: Role) -> Callable:
    def role_checker(
        current_user: UserContext = Depends(get_current_user),
    ) -> UserContext:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )

        return current_user

    return role_checker


def require_organization_access(
    organization_id: str,
    current_user: UserContext = Depends(get_current_user),
) -> UserContext:
    if current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this organization",
        )

    return current_user