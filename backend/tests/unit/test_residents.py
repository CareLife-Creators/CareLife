import unittest
from datetime import date, datetime, timezone
from unittest.mock import Mock

from pydantic import ValidationError

from app.application.interfaces.resident import (
    ResidentProfileRepository,
)
from app.application.schemas.resident import (
    ResidentProfileCreateRequest,
)
from app.application.use_cases.residents import (
    ResidentProfileService,
)
from app.domain.entities.resident import (
    ResidentProfile,
    ResidentProfileStatus,
)
from app.domain.entities.user_context import Role, UserContext


class ResidentProfileServiceTests(unittest.TestCase):

    def setUp(self):
        self.repository = Mock(spec=ResidentProfileRepository)

        self.service = ResidentProfileService(
            repository=self.repository,
        )

        self.user = UserContext(
            user_id="staff-1",
            role=Role.CARE_HOME_STAFF,
            organization_id="home-1",
            organization_ids=["home-1"],
        )

        timestamp = datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        )

        self.profile = ResidentProfile(
            id="resident-1",
            organization_id="home-1",
            full_name="Alice Resident",
            preferred_name="Alice",
            date_of_birth=date(1950, 1, 1),
            room_number="101",
            emergency_contact_name="Family Contact",
            emergency_contact_phone="01712345678",
            status=ResidentProfileStatus.ACTIVE,
            created_by="staff-1",
            updated_by="staff-1",
            created_at=timestamp,
            updated_at=timestamp,
        )

    def test_create_profile_calls_repository(self):
        self.repository.create_profile.return_value = self.profile

        request = ResidentProfileCreateRequest(
            full_name="Alice Resident",
            preferred_name="Alice",
            room_number="101",
            emergency_contact_name="Family Contact",
            emergency_contact_phone="01712345678",
        )

        result = self.service.create_profile(
            user=self.user,
            organization_id="home-1",
            request=request,
        )

        self.assertEqual(result.id, "resident-1")

        self.repository.create_profile.assert_called_once_with(
            user=self.user,
            organization_id="home-1",
            values=request.model_dump(),
        )

    def test_non_staff_cannot_create_profile(self):
        parent = UserContext(
            user_id="parent-1",
            role=Role.PARENT_GUARDIAN,
        )

        request = ResidentProfileCreateRequest(
            full_name="Alice Resident",
        )

        with self.assertRaises(PermissionError):
            self.service.create_profile(
                user=parent,
                organization_id="home-1",
                request=request,
            )

        self.repository.create_profile.assert_not_called()

    def test_empty_update_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.update_profile(
                user=self.user,
                organization_id="home-1",
                resident_id="resident-1",
                changes={},
            )

        self.repository.update_profile.assert_not_called()

    def test_unsupported_update_fields_are_rejected(self):
        with self.assertRaises(ValueError):
            self.service.update_profile(
                user=self.user,
                organization_id="home-1",
                resident_id="resident-1",
                changes={"diagnosis": "not permitted"},
            )

        self.repository.update_profile.assert_not_called()

    def test_blank_resident_name_is_rejected(self):
        with self.assertRaises(ValidationError):
            ResidentProfileCreateRequest(
                full_name="   ",
            )

    def test_future_date_of_birth_is_rejected(self):
        with self.assertRaises(ValidationError):
            ResidentProfileCreateRequest(
                full_name="Alice Resident",
                date_of_birth=date(2999, 1, 1),
            )

    def test_emergency_contact_must_be_complete(self):
        with self.assertRaises(ValidationError):
            ResidentProfileCreateRequest(
                full_name="Alice Resident",
                emergency_contact_name="Family Contact",
            )

    def test_clinical_field_is_rejected(self):
        with self.assertRaises(ValidationError):
            ResidentProfileCreateRequest(
                full_name="Alice Resident",
                diagnosis="This field is not part of a resident profile",
            )


if __name__ == "__main__":
    unittest.main()