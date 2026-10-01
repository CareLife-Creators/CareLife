from datetime import datetime, timedelta, timezone
import unittest

from app.domain.entities.password_reset_token import PasswordResetToken


class PasswordResetTokenTests(unittest.TestCase):
    def test_valid_token(self):
        now = datetime.now(timezone.utc)

        token = PasswordResetToken(
            user_id="user-1",
            token_hash="hashed-token",
            expires_at=now + timedelta(minutes=30),
        )

        self.assertTrue(token.is_valid(now))

    def test_expired_token_is_invalid(self):
        now = datetime.now(timezone.utc)

        token = PasswordResetToken(
            user_id="user-1",
            token_hash="hashed-token",
            expires_at=now - timedelta(minutes=1),
        )

        self.assertFalse(token.is_valid(now))

    def test_used_token_is_invalid(self):
        now = datetime.now(timezone.utc)

        token = PasswordResetToken(
            user_id="user-1",
            token_hash="hashed-token",
            expires_at=now + timedelta(minutes=30),
            used_at=now,
        )

        self.assertFalse(token.is_valid(now))

    def test_mark_used(self):
        now = datetime.now(timezone.utc)

        token = PasswordResetToken(
            user_id="user-1",
            token_hash="hashed-token",
            expires_at=now + timedelta(minutes=30),
        )

        token.mark_used(now)

        self.assertEqual(token.used_at, now)
        self.assertFalse(token.is_valid(now))


if __name__ == "__main__":
    unittest.main()