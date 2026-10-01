from datetime import datetime
from typing import Protocol

from app.domain.entities.password_reset_token import PasswordResetToken


class PasswordResetRepository(Protocol):
    def get_user_by_email(self, email: str) -> dict | None:
        ...

    def create_token(self, token: PasswordResetToken) -> None:
        ...

    def reset_password(
        self,
        token_hash: str,
        password_hash: str,
        now: datetime,
    ) -> bool:
        ...


class PasswordResetEmailSender(Protocol):
    def send_password_reset(
        self,
        email: str,
        reset_link: str,
    ) -> None:
        ...
        