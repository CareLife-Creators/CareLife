from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from app.application.interfaces.password_reset import (
    PasswordResetEmailSender,
    PasswordResetRepository,
)
from app.core.security import (
    generate_password_reset_token,
    hash_password,
    hash_password_reset_token,
)
from app.domain.entities.password_reset_token import PasswordResetToken


class PasswordResetService:
    def __init__(
        self,
        repository: PasswordResetRepository,
        email_sender: PasswordResetEmailSender,
        token_expire_minutes: int,
        reset_link_base_url: str,
    ):
        self.repository = repository
        self.email_sender = email_sender
        self.token_expire_minutes = token_expire_minutes
        self.reset_link_base_url = reset_link_base_url

    def request_reset(self, email: str) -> str:
        normalized_email = email.strip().lower()

        user = self.repository.get_user_by_email(
            normalized_email
        )

        message = (
            "If an account exists for this email, "
            "a password reset link has been sent."
        )

        if user is None:
            return message

        raw_token = generate_password_reset_token()

        now = datetime.now(timezone.utc)

        token = PasswordResetToken(
            user_id=user["id"],
            token_hash=hash_password_reset_token(raw_token),
            expires_at=now + timedelta(
                minutes=self.token_expire_minutes
            ),
        )

        self.repository.create_token(token)

        query = urlencode({"token": raw_token})
        reset_link = f"{self.reset_link_base_url}?{query}"

        self.email_sender.send_password_reset(
            normalized_email,
            reset_link,
        )

        return message

    def reset_password(
        self,
        token: str,
        new_password: str,
    ) -> str:
        token_hash = hash_password_reset_token(token)
        password_hash = hash_password(new_password)
        now = datetime.now(timezone.utc)

        success = self.repository.reset_password(
            token_hash=token_hash,
            password_hash=password_hash,
            now=now,
        )

        if not success:
            raise ValueError(
                "Invalid or expired password reset token"
            )

        return "Password reset successfully."