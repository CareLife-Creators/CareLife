import unittest

from app.application.use_cases.login import LoginService
from app.core.security import hash_password
from app.domain.entities.user import User


class FakeUserRepository:
    def __init__(self, user: User | None):
        self.user = user

    def get_by_email(self, email: str) -> User | None:
        if self.user and self.user.email == email:
            return self.user
        return None


class LoginServiceTests(unittest.TestCase):
    def make_user(self, *, is_active: bool = True) -> User:
        return User(
            id="user-1",
            email="parent@example.com",
            password_hash=hash_password("StrongPassword123!"),
            role_name="parent_guardian",
            is_active=is_active,
        )

    def test_active_user_can_login(self):
        user = self.make_user()
        service = LoginService(FakeUserRepository(user))

        result = service.login(
            " PARENT@example.com ",
            "StrongPassword123!",
        )

        self.assertEqual(result.id, user.id)

    def test_inactive_user_cannot_login(self):
        service = LoginService(
            FakeUserRepository(self.make_user(is_active=False))
        )

        with self.assertRaisesRegex(
            ValueError,
            "Invalid email or password",
        ):
            service.login(
                "parent@example.com",
                "StrongPassword123!",
            )

    def test_wrong_password_is_rejected(self):
        service = LoginService(FakeUserRepository(self.make_user()))

        with self.assertRaisesRegex(
            ValueError,
            "Invalid email or password",
        ):
            service.login(
                "parent@example.com",
                "WrongPassword123!",
            )


if __name__ == "__main__":
    unittest.main()
