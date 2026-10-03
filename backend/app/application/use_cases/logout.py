from datetime import datetime, timezone

from app.application.interfaces.session import SessionRepository
from app.core.security import decode_access_token


class LogoutService:
    def __init__(self, repository: SessionRepository):
        self.repository = repository

    def logout(self, token: str) -> None:
        payload = decode_access_token(token)

        expires_at = datetime.fromtimestamp(
            payload["exp"],
            tz=timezone.utc,
        )

        revoked_at = datetime.now(timezone.utc)

        self.repository.revoke_token(
            token_id=payload["jti"],
            user_id=payload["sub"],
            revoked_at=revoked_at,
            expires_at=expires_at,
        )