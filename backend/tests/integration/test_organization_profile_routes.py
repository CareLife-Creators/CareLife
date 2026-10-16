import unittest
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.application.use_cases.organization_profile import (
    OrganizationProfileService,
)
from app.domain.entities.organization import OrganizationStatus
from app.domain.entities.organization_profile import (
    OrganizationProfile,
)
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import (
    get_current_user,
)
from app.presentation.api.dependencies.organization_profile import (
    get_organization_profile_service,
)
from main import app


def make_profile() -> OrganizationProfile:
    return OrganizationProfile(
        organization_id="org-1",
        organization_name="Sunshine Daycare",
        organization_type="daycare",
        description="Childcare center",
        location="Dhaka",
        contact="+8801712345678",
        capacity=20,
        age_range="6 months–5 years",
        opening_hours="8:00 AM–6:00 PM",
        facilities="CCTV, playground",
        fees="BDT 6,000 per month",
        status=OrganizationStatus.VERIFIED,
        updated_at=datetime.now(timezone.utc),
    )


class FakeOrganizationProfileRepository:

    def __init__(self):
        self.profile = make_profile()

    def get_for_staff(self, organization_id):
        if organization_id != self.profile.organization_id:
            return None
        return self.profile

    def get_public(self, organization_id):
        profile = self.get_for_staff(organization_id)

        if (
            profile is None
            or profile.status != OrganizationStatus.VERIFIED
        ):
            return None

        return profile

    def update_profile(
        self,
        organization_id,
        changes,
        updated_by,
    ):
        if self.get_for_staff(organization_id) is None:
            return None

        self.profile = self.profile.model_copy(
            update={
                **changes,
                "updated_at": datetime.now(timezone.utc),
            }
        )

        return self.profile


class OrganizationProfileRouteTests(unittest.TestCase):

    def setUp(self):
        self.repository = FakeOrganizationProfileRepository()
        self.service = OrganizationProfileService(
            self.repository
        )

        self.current_user = UserContext(
            user_id="staff-1",
            role=Role.DAYCARE_STAFF,
            organization_id="org-1",
            organization_ids=["org-1"],
        )

        app.dependency_overrides[
            get_organization_profile_service
        ] = lambda: self.service

        app.dependency_overrides[
            get_current_user
        ] = lambda: self.current_user

        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_staff_can_view_own_organization_profile(self):
        response = self.client.get(
            "/organizations/org-1/profile"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["organization_name"],
            "Sunshine Daycare",
        )
        self.assertEqual(response.json()["capacity"], 20)

    def test_staff_can_update_organization_profile(self):
        response = self.client.patch(
            "/organizations/org-1/profile",
            json={
                "organization_name": "Sunshine Daycare Center",
                "capacity": 35,
                "facilities": "CCTV, playground, meals",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["organization_name"],
            "Sunshine Daycare Center",
        )
        self.assertEqual(response.json()["capacity"], 35)
        self.assertEqual(
            response.json()["facilities"],
            "CCTV, playground, meals",
        )

    def test_non_staff_cannot_manage_organization_profile(self):
        self.current_user = UserContext(
            user_id="parent-1",
            role=Role.PARENT_GUARDIAN,
            organization_id="org-1",
            organization_ids=["org-1"],
        )

        response = self.client.get(
            "/organizations/org-1/profile"
        )

        self.assertEqual(response.status_code, 403)

    def test_staff_without_membership_is_rejected(self):
        self.current_user = UserContext(
            user_id="staff-2",
            role=Role.DAYCARE_STAFF,
            organization_ids=[],
        )

        response = self.client.patch(
            "/organizations/org-1/profile",
            json={"description": "Unauthorized update"},
        )

        self.assertEqual(response.status_code, 403)

    def test_public_profile_excludes_internal_fields(self):
        response = self.client.get(
            "/organizations/org-1/public-profile"
        )

        self.assertEqual(response.status_code, 200)

        body = response.json()

        self.assertEqual(body["organization_id"], "org-1")
        self.assertEqual(body["capacity"], 20)
        self.assertIn("facilities", body)

        self.assertNotIn("license_number", body)
        self.assertNotIn("license_expiry_date", body)
        self.assertNotIn("submitted_by", body)
        self.assertNotIn("status", body)

    def test_unknown_profile_is_rejected_for_non_member(self):
        response = self.client.get(
            "/organizations/missing-org/profile"
        )

        # Membership is checked before resource lookup, avoiding
        # organization-ID enumeration by users without access.
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
