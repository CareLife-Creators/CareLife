from fastapi import Depends, Header, HTTPException, status

from app.core.security import decode_access_token
from app.domain.entities.user_context import Role, UserContext
from app.infrastructure.repositories.session_repository import (
    PostgresSessionRepository,
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

    session_repository = PostgresSessionRepository()

    if session_repository.is_token_revoked(payload["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication session has been revoked",
        )

    return UserContext(
        user_id=payload["sub"],
        role=Role.PARENT_GUARDIAN,
        organization_id=None,
    )