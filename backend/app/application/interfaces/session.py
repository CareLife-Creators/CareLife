from datetime import datetime
from typing import Protocol


class SessionRepository(Protocol):
    def revoke_token(
        self,
        token_id: str,
        user_id: str,
        revoked_at: datetime,
        expires_at: datetime,
    ) -> None:
        ...

    def is_token_revoked(self, token_id: str) -> bool:
        ...