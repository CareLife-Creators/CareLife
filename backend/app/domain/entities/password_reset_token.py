from datetime import datetime, timezone

from pydantic import BaseModel


class PasswordResetToken(BaseModel):
    user_id: str
    token_hash: str
    expires_at: datetime
    used_at: datetime | None = None

    def is_valid(self, now: datetime | None = None) -> bool:
        current_time = now or datetime.now(timezone.utc)

        if self.used_at is not None:
            return False

        return current_time < self.expires_at

    def mark_used(self, now: datetime | None = None) -> None:
        self.used_at = now or datetime.now(timezone.utc)