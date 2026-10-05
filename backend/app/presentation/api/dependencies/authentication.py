from fastapi import Depends, Header, HTTPException, status

from app.core.security import decode_access_token
from app.domain.entities.user_context import Role, UserContext
from app.infrastructure.repositories.session_repository import (
    PostgresSessionRepository,
)
from app.infrastructure.repositories.user_repository import (
    PostgresUserRepository,
)


def get_bearer_token(
    authorization: str | None = Header(default=None),
) -> str:

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme",
        )

    token = authorization[7:].strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    return token


def get_authenticated_user(
    token: str = Depends(get_bearer_token),
) -> UserContext:

    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        ) from exc

    token_id = payload.get("jti")
    user_id = payload.get("sub")

    if not token_id or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    session_repository = PostgresSessionRepository()

    if session_repository.is_token_revoked(token_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication session has been revoked",
        )

    user_repository = PostgresUserRepository()

    user = user_repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )

    try:
        role = Role(user.role_name)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User has an invalid role",
        ) from exc

    return UserContext(
        user_id=user.id,
        role=role,
        organization_id=user.organization_id,
        organization_ids=user.organization_ids,
    )