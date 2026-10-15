import unittest

from fastapi.testclient import TestClient

from app.application.use_cases.user_profile import UserProfileService
from app.domain.entities.user import User
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import (
    get_current_user,
)
from app.presentation.api.dependencies.user_profile import (
    get_user_profile_service,
)
from main import app


class FakeUserRepository:
    def __init__(self):
        self.user = User(
            id="user-1",
            email="rafi@example.com",
            password_hash="secret-hash",
            role_name="parent_guardian",
            full_name="Rafi",
            phone="+8801712345678",
            is_active=True,
        )

    def get_by_id(self, user_id: str) -> User | None:
        if user_id != self.user.id:
            return None

        return self.user

    def update_profile(
        self,
        user_id: str,
        changes: dict[str, str | None],
    ) -> User | None:
        if user_id != self.user.id:
            return None

        self.user = self.user.model_copy(update=changes)
        return self.user


class UserProfileRouteTests(unittest.TestCase):
    def setUp(self):
        self.repository = FakeUserRepository()
        self.service = UserProfileService(self.repository)

        self.current_user = UserContext(
            user_id="user-1",
            role=Role.PARENT_GUARDIAN,
        )

        app.dependency_overrides[
            get_user_profile_service
        ] = lambda: self.service

        app.dependency_overrides[
            get_current_user
        ] = lambda: self.current_user

        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_unauthenticated_request_is_rejected(self):
        app.dependency_overrides.pop(
            get_current_user,
            None,
        )

        response = self.client.get("/users/me/profile")

        self.assertEqual(response.status_code, 401)

    def test_user_can_view_own_profile(self):
        response = self.client.get("/users/me/profile")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user_id"], "user-1")
        self.assertEqual(
            response.json()["email"],
            "rafi@example.com",
        )
        self.assertEqual(response.json()["full_name"], "Rafi")
        self.assertEqual(
            response.json()["role"],
            "parent_guardian",
        )

        self.assertNotIn("password_hash", response.json())
        self.assertNotIn("is_active", response.json())

    def test_user_can_update_own_profile(self):
        response = self.client.patch(
            "/users/me/profile",
            json={
                "full_name": "Rafi Azim",
                "phone": "+8801812345678",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["full_name"],
            "Rafi Azim",
        )
        self.assertEqual(
            response.json()["phone"],
            "+8801812345678",
        )

    def test_role_cannot_be_changed(self):
        response = self.client.patch(
            "/users/me/profile",
            json={"role": "carelife_admin"},
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            self.repository.user.role_name,
            "parent_guardian",
        )

    def test_invalid_phone_is_rejected(self):
        response = self.client.patch(
            "/users/me/profile",
            json={"phone": "not-a-phone"},
        )

        self.assertEqual(response.status_code, 422)

    def test_empty_update_is_rejected(self):
        response = self.client.patch(
            "/users/me/profile",
            json={},
        )

        self.assertEqual(response.status_code, 422)

    def test_other_users_profile_path_is_not_available(self):
        response = self.client.get(
            "/users/user-2/profile"
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()