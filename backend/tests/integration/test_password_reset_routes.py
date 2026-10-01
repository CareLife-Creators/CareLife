import unittest
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

from main import app
from app.presentation.api.dependencies.password_reset import (
    get_password_reset_service,
)
from app.application.use_cases.password_reset import (
    PasswordResetService,
)


class FakeRepository:
    def __init__(self):
        self.users = {
            "user-1": {
                "id": "user-1",
                "email": "user@example.com",
                "password_hash": "old-hash",
            }
        }
        self.tokens = {}

    def get_user_by_email(self, email):
        for user in self.users.values():
            if user["email"].lower() == email.lower():
                return user

        return None

    def create_token(self, token):
        self.tokens[token.token_hash] = token

    def reset_password(
        self,
        token_hash,
        password_hash,
        now,
    ):
        token = self.tokens.get(token_hash)

        if token is None:
            return False

        if token.used_at is not None:
            return False

        if now >= token.expires_at:
            return False

        self.users[token.user_id]["password_hash"] = password_hash
        token.mark_used(now)

        return True


class FakeEmailSender:
    def __init__(self):
        self.sent = []

    def send_password_reset(self, email, reset_link):
        self.sent.append(
            {
                "email": email,
                "reset_link": reset_link,
            }
        )


class PasswordResetRouteTests(unittest.TestCase):
    def setUp(self):
        self.repository = FakeRepository()
        self.email_sender = FakeEmailSender()

        self.service = PasswordResetService(
            repository=self.repository,
            email_sender=self.email_sender,
            token_expire_minutes=30,
            reset_link_base_url=(
                "http://localhost:3000/reset-password"
            ),
        )

        app.dependency_overrides[
            get_password_reset_service
        ] = lambda: self.service

        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_reset_request(self):
        response = self.client.post(
            "/auth/password-reset/request",
            json={
                "email": "user@example.com"
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            len(self.email_sender.sent),
            1,
        )

    def test_unknown_email_does_not_reveal_account(self):
        response = self.client.post(
            "/auth/password-reset/request",
            json={
                "email": "missing@example.com"
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "If an account exists",
            response.json()["message"],
        )

    def test_invalid_token_returns_400(self):
        response = self.client.post(
            "/auth/password-reset/confirm",
            json={
                "token": "invalid-token",
                "new_password": "NewPassword123!",
            },
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_valid_token_resets_password(self):
        self.service.request_reset(
            "user@example.com"
        )

        link = self.email_sender.sent[0]["reset_link"]

        token = parse_qs(
            urlparse(link).query
        )["token"][0]

        response = self.client.post(
            "/auth/password-reset/confirm",
            json={
                "token": token,
                "new_password": "NewPassword123!",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()["message"],
            "Password reset successfully.",
        )

    def test_used_token_returns_400(self):
        self.service.request_reset(
            "user@example.com"
        )

        link = self.email_sender.sent[0]["reset_link"]

        token = parse_qs(
            urlparse(link).query
        )["token"][0]

        first_response = self.client.post(
            "/auth/password-reset/confirm",
            json={
                "token": token,
                "new_password": "NewPassword123!",
            },
        )

        self.assertEqual(
            first_response.status_code,
            200,
        )

        second_response = self.client.post(
            "/auth/password-reset/confirm",
            json={
                "token": token,
                "new_password": "AnotherPassword123!",
            },
        )

        self.assertEqual(
            second_response.status_code,
            400,
        )


if __name__ == "__main__":
    unittest.main()