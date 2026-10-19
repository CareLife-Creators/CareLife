import unittest

from app.application.use_cases.signup import (
    PUBLIC_SIGNUP_ROLES,
    SignupService,
)


class FakeUserRepository:
    def __init__(self):
        self.users = {}

    def get_by_email(self, email):
        return self.users.get(email)

    def create(self, user):
        self.users[user.email] = user
        return user

    def create_if_not_exists(self, user):
        if user.email in self.users:
            return None
        return self.create(user)


class SignupServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = FakeUserRepository()
        self.service = SignupService(self.repository)

    def test_each_public_role_can_sign_up(self):
        for index, role in enumerate(sorted(PUBLIC_SIGNUP_ROLES)):
            with self.subTest(role=role):
                user = self.service.signup(
                    email=f"user{index}@example.com",
                    password="StrongPassword123!",
                    full_name="Example User",
                    phone="+8801712345678",
                    role=role,
                )
                self.assertEqual(user.role_name, role)

    def test_staff_and_admin_roles_are_rejected_by_service(self):
        for role in (
            "daycare_staff",
            "orphanage_staff",
            "care_home_staff",
            "carelife_admin",
        ):
            with self.subTest(role=role):
                with self.assertRaisesRegex(ValueError, "Invalid signup role"):
                    self.service.signup(
                        email=f"{role}@example.com",
                        password="StrongPassword123!",
                        full_name="Example User",
                        phone="+8801712345678",
                        role=role,
                    )

    def test_duplicate_email_does_not_create_a_second_user(self):
        first = self.service.signup(
            email="same@example.com",
            password="StrongPassword123!",
            full_name="First User",
            phone="+8801712345678",
            role="parent_guardian",
        )
        duplicate = self.service.signup(
            email=" SAME@example.com ",
            password="DifferentPassword123!",
            full_name="Second User",
            phone="+8801812345678",
            role="donor_supporter",
        )

        self.assertIsNotNone(first)
        self.assertIsNone(duplicate)
        self.assertEqual(len(self.repository.users), 1)
        self.assertEqual(
            self.repository.users["same@example.com"].role_name,
            "parent_guardian",
        )


if __name__ == "__main__":
    unittest.main()
