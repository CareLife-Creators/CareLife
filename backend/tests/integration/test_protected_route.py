import unittest

from fastapi.testclient import TestClient

from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import get_current_user
from main import app


class ProtectedRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_no_authenticated_user_is_rejected(self):
        response = self.client.get("/protected/admin")

        self.assertEqual(response.status_code, 401)

    def test_admin_user_is_allowed(self):
        admin_user = UserContext(
            user_id="admin-1",
            role=Role.CARELIFE_ADMIN,
        )

        app.dependency_overrides[get_current_user] = lambda: admin_user

        response = self.client.get("/protected/admin")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user_id"], "admin-1")
        self.assertEqual(response.json()["role"], "carelife_admin")

    def test_non_admin_user_is_rejected(self):
        parent_user = UserContext(
            user_id="parent-1",
            role=Role.PARENT_GUARDIAN,
        )

        app.dependency_overrides[get_current_user] = lambda: parent_user

        response = self.client.get("/protected/admin")

        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()