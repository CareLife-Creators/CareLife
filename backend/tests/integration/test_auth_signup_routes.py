import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.application.use_cases.login import LoginService
from app.application.use_cases.signup import SignupService
from app.core.security import hash_password
from app.domain.entities.user import User
from app.presentation.api.dependencies.login import get_login_service
from app.presentation.api.dependencies.signup import get_signup_service
from main import app


class FakeUserRepository:
    def __init__(self):
        self.users = {}

    def get_by_email(self, email):
        return self.users.get(email.strip().lower())

    def get_by_id(self, user_id):
        for user in self.users.values():
            if user.id == user_id:
                return user
        return None

    def create(self, user):
        self.users[user.email] = user
        return user

    def create_if_not_exists(self, user):
        if user.email in self.users:
            return None
        return self.create(user)

    def update_profile(self, user_id, changes):
        user = self.get_by_id(user_id)
        if user is None:
            return None
        updated = user.model_copy(update=changes)
        self.users[updated.email] = updated
        return updated


class AuthenticationRoutesTests(unittest.TestCase):
    def setUp(self):
        self.repository = FakeUserRepository()
        self.signup_service = SignupService(self.repository)
        self.login_service = LoginService(self.repository)
        app.dependency_overrides[get_signup_service] = (
            lambda: self.signup_service
        )
        app.dependency_overrides[get_login_service] = (
            lambda: self.login_service
        )
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def signup_payload(self, email, role="parent_guardian"):
        return {
            "email": email,
            "password": "StrongPassword123!",
            "full_name": "Example User",
            "phone": "+8801712345678",
            "role": role,
        }

    def test_signup_accepts_only_the_four_public_roles(self):
        allowed_roles = (
            "parent_guardian",
            "donor_supporter",
            "independent_caregiver",
            "family_representative",
        )
        for index, role in enumerate(allowed_roles):
            with self.subTest(role=role):
                email = f"allowed{index}@example.com"
                response = self.client.post(
                    "/auth/signup",
                    json=self.signup_payload(email, role),
                )
                self.assertEqual(response.status_code, 201)
                self.assertEqual(
                    response.json(),
                    {"message": "Signup request received."},
                )
                self.assertEqual(self.repository.users[email].role_name, role)
                self.assertNotIn("user_id", response.json())

    def test_signup_rejects_staff_admin_and_unknown_roles(self):
        for role in (
            "daycare_staff",
            "orphanage_staff",
            "care_home_staff",
            "carelife_admin",
            "unknown_role",
        ):
            with self.subTest(role=role):
                response = self.client.post(
                    "/auth/signup",
                    json=self.signup_payload(f"{role}@example.com", role),
                )
                self.assertEqual(response.status_code, 422)

    def test_duplicate_email_returns_same_generic_response(self):
        payload = self.signup_payload("same@example.com")
        first = self.client.post("/auth/signup", json=payload)
        duplicate = self.client.post(
            "/auth/signup",
            json={**payload, "password": "AnotherPassword123!"},
        )

        self.assertEqual(first.status_code, 201)
        self.assertEqual(duplicate.status_code, 201)
        self.assertEqual(first.json(), duplicate.json())
        self.assertEqual(
            first.json(),
            {"message": "Signup request received."},
        )
        self.assertEqual(len(self.repository.users), 1)

    def test_login_response_includes_actual_role(self):
        user = User(
            id="donor-user-1",
            email="donor@example.com",
            password_hash=hash_password("StrongPassword123!"),
            role_name="donor_supporter",
            full_name="Donor User",
            phone="+8801712345678",
        )
        self.repository.create(user)

        with patch(
            "app.presentation.api.routes.login.create_access_token",
            return_value="signed-token",
        ):
            response = self.client.post(
                "/auth/login",
                json={
                    "email": "donor@example.com",
                    "password": "StrongPassword123!",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["role"], "donor_supporter")
        self.assertEqual(response.json()["access_token"], "signed-token")

    def test_login_keeps_generic_invalid_credentials_error(self):
        response = self.client.post(
            "/auth/login",
            json={
                "email": "missing@example.com",
                "password": "StrongPassword123!",
            },
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {"detail": "Invalid email or password"},
        )


if __name__ == "__main__":
    unittest.main()
