import unittest
from datetime import datetime, timezone
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.application.use_cases.residents import (
    ResidentProfileService,
)
from app.domain.entities.resident import (
    ResidentProfile,
    ResidentProfileStatus,
)
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import (
    get_current_user,
)
from app.presentation.api.dependencies.resident import (
    get_resident_profile_service,
)
from main import app


class ResidentProfileRouteTests(unittest.TestCase):

    def setUp(self):
        self.service = Mock(spec=ResidentProfileService)

        self.current_user = UserContext(
            user_id="staff-1",
            role=Role.CARE_HOME_STAFF,
            organization_id="home-1",
            organization_ids=["home-1"],
        )

        app.dependency_overrides[get_current_user] = (
            lambda: self.current_user
        )

        app.dependency_overrides[
            get_resident_profile_service
        ] = lambda: self.service

        self.client = TestClient(app)

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
            date_of_birth=None,
            room_number="101",
            emergency_contact_name=None,
            emergency_contact_phone=None,
            status=ResidentProfileStatus.ACTIVE,
            created_by="staff-1",
            updated_by="staff-1",
            created_at=timestamp,
            updated_at=timestamp,
        )

    def tearDown(self):
        app.dependency_overrides.pop(
            get_current_user,
            None,
        )

        app.dependency_overrides.pop(
            get_resident_profile_service,
            None,
        )

    def test_create_resident_returns_201(self):
        self.service.create_profile.return_value = self.profile

        response = self.client.post(
            "/elder-care/organizations/home-1/residents",
            json={
                "full_name": "Alice Resident",
                "preferred_name": "Alice",
                "room_number": "101",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()["id"],
            "resident-1",
        )
        self.assertEqual(
            response.json()["organization_id"],
            "home-1",
        )
        self.assertEqual(
            response.json()["status"],
            "active",
        )

        self.service.create_profile.assert_called_once()

    def test_clinical_fields_are_rejected(self):
        response = self.client.post(
            "/elder-care/organizations/home-1/residents",
            json={
                "full_name": "Alice Resident",
                "diagnosis": "not permitted",
            },
        )

        self.assertEqual(response.status_code, 422)
        self.service.create_profile.assert_not_called()

    def test_invalid_name_is_rejected(self):
        response = self.client.post(
            "/elder-care/organizations/home-1/residents",
            json={
                "full_name": "   ",
            },
        )

        self.assertEqual(response.status_code, 422)
        self.service.create_profile.assert_not_called()

    def test_non_staff_user_receives_403(self):
        self.current_user = UserContext(
            user_id="parent-1",
            role=Role.PARENT_GUARDIAN,
        )

        response = self.client.get(
            "/elder-care/organizations/home-1/residents"
        )

        self.assertEqual(response.status_code, 403)
        self.service.list_profiles.assert_not_called()

    def test_missing_resident_returns_404(self):
        self.service.get_profile.side_effect = LookupError(
            "Resident profile not found"
        )

        response = self.client.get(
            "/elder-care/organizations/home-1/residents/"
            "missing-resident"
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()