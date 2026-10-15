import unittest
from unittest.mock import Mock

from app.application.schemas.user_profile import (
    UserProfileUpdateRequest,
)
from app.application.use_cases.user_profile import UserProfileService
from app.domain.entities.user import User


def make_user(**overrides) -> User:
    data = {
        "id": "user-1",
        "email": "rafi@example.com",
        "password_hash": "hashed-value",
        "role_name": "parent_guardian",
        "full_name": "Rafi",
        "phone": "+8801712345678",
        "is_active": True,
    }
    data.update(overrides)
    return User(**data)


class UserProfileServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = Mock()
        self.service = UserProfileService(self.repository)
        self.user = make_user()
        self.repository.get_by_id.return_value = self.user

    def test_get_profile_returns_existing_user(self):
        result = self.service.get_profile("user-1")

        self.assertEqual(result.id, "user-1")
        self.assertEqual(result.full_name, "Rafi")
        self.repository.get_by_id.assert_called_once_with("user-1")

    def test_missing_profile_is_rejected(self):
        self.repository.get_by_id.return_value = None

        with self.assertRaises(LookupError):
            self.service.get_profile("missing-user")

    def test_inactive_profile_is_not_returned(self):
        self.repository.get_by_id.return_value = make_user(
            is_active=False
        )

        with self.assertRaises(LookupError):
            self.service.get_profile("user-1")

    def test_update_profile_saves_permitted_fields(self):
        updated_user = make_user(full_name="Rafi Azim")
        self.repository.update_profile.return_value = updated_user

        result = self.service.update_profile(
            "user-1",
            {"full_name": "Rafi Azim"},
        )

        self.assertEqual(result.full_name, "Rafi Azim")
        self.repository.update_profile.assert_called_once_with(
            "user-1",
            {"full_name": "Rafi Azim"},
        )

    def test_empty_update_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.update_profile("user-1", {})

        self.repository.update_profile.assert_not_called()

    def test_role_cannot_be_updated(self):
        with self.assertRaises(ValueError):
            self.service.update_profile(
                "user-1",
                {"role_name": "carelife_admin"},
            )

        self.repository.update_profile.assert_not_called()

    def test_missing_user_during_update_is_rejected(self):
        self.repository.update_profile.return_value = None

        with self.assertRaises(LookupError):
            self.service.update_profile(
                "user-1",
                {"full_name": "New Name"},
            )

    def test_inactive_user_cannot_update_profile(self):
        self.repository.get_by_id.return_value = make_user(
            is_active=False
        )

        with self.assertRaises(LookupError):
            self.service.update_profile(
                "user-1",
                {"full_name": "New Name"},
            )

        self.repository.update_profile.assert_not_called()


class UserProfileSchemaTests(unittest.TestCase):
    def test_valid_profile_update(self):
        request = UserProfileUpdateRequest(
            full_name="  Rafi Azim  ",
            phone="+8801712345678",
        )

        self.assertEqual(request.full_name, "Rafi Azim")
        self.assertEqual(request.phone, "+8801712345678")

    def test_blank_name_can_be_cleared(self):
        request = UserProfileUpdateRequest(full_name="   ")

        self.assertIsNone(request.full_name)

    def test_invalid_phone_is_rejected(self):
        with self.assertRaises(ValueError):
            UserProfileUpdateRequest(phone="not-a-phone")

    def test_empty_request_is_rejected(self):
        with self.assertRaises(ValueError):
            UserProfileUpdateRequest()

    def test_role_is_not_an_editable_field(self):
        with self.assertRaises(ValueError):
            UserProfileUpdateRequest(
                role="carelife_admin"
            )


if __name__ == "__main__":
    unittest.main()