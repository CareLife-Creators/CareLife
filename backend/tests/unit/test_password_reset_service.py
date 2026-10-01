import unittest
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse
from app.core.security import password_hash
from app.application.use_cases.password_reset import (
    PasswordResetService,
)
from app.domain.entities.password_reset_token import (
    PasswordResetToken,
)
from app.core.security import hash_password_reset_token


class FakePasswordResetRepository:
    def __init__(self):
        self.users = {
            "user-1": {
                "id": "user-1",
                "email": "user@example.com",
                "password_hash": "old-password-hash",
            }
        }

        self.tokens: dict[str, PasswordResetToken] = {}

    def get_user_by_email(self, email: str):
        for user in self.users.values():
            if user["email"].lower() == email.lower():
                return user

        return None

    def create_token(self, token: PasswordResetToken):
        self.tokens[token.token_hash] = token

    def reset_password(
        self,
        token_hash: str,
        password_hash: str,
        now: datetime,
    ) -> bool:
        token = self.tokens.get(token_hash)

        if token is None:
            return False

        if token.used_at is not None:
            return False

        if now >= token.expires_at:
            return False

        user = self.users.get(token.user_id)

        if user is None:
            return False

        user["password_hash"] = password_hash
        token.mark_used(now)

        return True


class FakeEmailSender:
    def __init__(self):
        self.sent = []

    def send_password_reset(
        self,
        email: str,
        reset_link: str,
    ):
        self.sent.append(
            {
                "email": email,
                "reset_link": reset_link,
            }
        )


class PasswordResetServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = FakePasswordResetRepository()
        self.email_sender = FakeEmailSender()

        self.service = PasswordResetService(
            repository=self.repository,
            email_sender=self.email_sender,
            token_expire_minutes=30,
            reset_link_base_url=(
                "http://localhost:3000/reset-password"
            ),
        )

    def test_registered_email_triggers_reset_email(self):
        message = self.service.request_reset(
            "user@example.com"
        )

        self.assertIn(
            "password reset link has been sent",
            message,
        )

        self.assertEqual(len(self.email_sender.sent), 1)

        sent = self.email_sender.sent[0]

        self.assertEqual(
            sent["email"],
            "user@example.com",
        )

        parsed = urlparse(sent["reset_link"])
        token = parse_qs(parsed.query)["token"][0]

        token_hash = hash_password_reset_token(token)

        self.assertIn(
            token_hash,
            self.repository.tokens,
        )

        self.assertNotEqual(
            token,
            token_hash,
        )

    def test_unknown_email_returns_generic_message(self):
        message = self.service.request_reset(
            "unknown@example.com"
        )

        self.assertIn(
            "If an account exists",
            message,
        )

        self.assertEqual(
            len(self.email_sender.sent),
            0,
        )

    def test_valid_token_resets_password(self):
        self.service.request_reset(
            "user@example.com"
        )

        reset_link = self.email_sender.sent[0]["reset_link"]

        token = parse_qs(
            urlparse(reset_link).query
        )["token"][0]

        message = self.service.reset_password(
            token=token,
            new_password="NewPassword123!",
        )

        self.assertEqual(
            message,
            "Password reset successfully.",
        )

        self.assertTrue(
            password_hash.verify(
               "NewPassword123!",
                self.repository.users["user-1"]["password_hash"],
            )
        )


    def test_invalid_token_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.reset_password(
                token="invalid-token",
                new_password="NewPassword123!",
            )

    def test_used_token_cannot_be_reused(self):
        self.service.request_reset(
            "user@example.com"
        )

        reset_link = self.email_sender.sent[0]["reset_link"]

        token = parse_qs(
            urlparse(reset_link).query
        )["token"][0]

        self.service.reset_password(
            token=token,
            new_password="NewPassword123!",
        )

        with self.assertRaises(ValueError):
            self.service.reset_password(
                token=token,
                new_password="AnotherPassword123!",
            )

    def test_expired_token_is_rejected(self):
        now = datetime.now(timezone.utc)

        token = PasswordResetToken(
            user_id="user-1",
            token_hash=hash_password_reset_token(
                "expired-token"
            ),
            expires_at=now - timedelta(minutes=1),
        )

        self.repository.create_token(token)

        with self.assertRaises(ValueError):
            self.service.reset_password(
                token="expired-token",
                new_password="NewPassword123!",
            )


if __name__ == "__main__":
    unittest.main()