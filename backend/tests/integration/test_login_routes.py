import unittest

import jwt
from fastapi.testclient import TestClient

from main import app
from app.application.use_cases.login import LoginService
from app.core.config import get_settings
from app.core.security import hash_password
from app.presentation.api.dependencies.login import get_login_service


class FakeRepository:
    def __init__(self):
        self.user = {
            "id": "user-1",
            "email": "user@example.com",
            "password_hash": hash_password("CorrectPassword123!"),
        }

    def get_user_by_email(self, email: str) -> dict | None:
        if email.strip().lower() == self.user["email"]:
            return self.user
        return None


class LoginRouteTests(unittest.TestCase):
    def setUp(self):
        self.repository = FakeRepository()
        self.service = LoginService(repository=self.repository)
        app.dependency_overrides[get_login_service] = lambda: self.service
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_valid_credentials_return_access_token(self):
        response = self.client.post(
            "/auth/login",
            json={
                "email": "user@example.com",
                "password": "CorrectPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["token_type"], "bearer")
        self.assertTrue(body["access_token"])

        payload = jwt.decode(
            body["access_token"],
            get_settings().secret_key_value,
            algorithms=["HS256"],
        )
        self.assertEqual(payload["sub"], "user-1")
        self.assertEqual(payload["type"], "access")
        self.assertGreater(payload["exp"], payload["iat"])

    def test_wrong_password_returns_safe_401(self):
        response = self.client.post(
            "/auth/login",
            json={
                "email": "user@example.com",
                "password": "WrongPassword123!",
            },
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json()["detail"],
            "Invalid email or password.",
        )
        self.assertEqual(
            response.headers.get("www-authenticate"),
            "Bearer",
        )

    def test_unknown_email_returns_same_safe_401(self):
        response = self.client.post(
            "/auth/login",
            json={
                "email": "unknown@example.com",
                "password": "WrongPassword123!",
            },
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json()["detail"],
            "Invalid email or password.",
        )

    def test_invalid_email_returns_422(self):
        response = self.client.post(
            "/auth/login",
            json={
                "email": "not-an-email",
                "password": "SomePassword123!",
            },
        )

        self.assertEqual(response.status_code, 422)

    def test_empty_password_returns_422(self):
        response = self.client.post(
            "/auth/login",
            json={
                "email": "user@example.com",
                "password": "",
            },
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
