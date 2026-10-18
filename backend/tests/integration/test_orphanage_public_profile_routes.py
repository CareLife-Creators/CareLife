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
from app.presentation.api.dependencies.organization_profile import (
    get_organization_profile_service,
)
from main import app


def make_profile(
    organization_type: str = "orphanage",
    status: OrganizationStatus = OrganizationStatus.VERIFIED,
) -> OrganizationProfile:
    return OrganizationProfile(
        organization_id="org-53",
        organization_name="Hope Orphanage",
        organization_type=organization_type,
        description="Support and care for children.",
        location="Dhaka",
        contact="+8801700000000",
        capacity=30,
        age_range=None,
        opening_hours=None,
        facilities="Study room and recreation area",
        fees=None,
        status=status,
        updated_at=datetime.now(timezone.utc),
    )


class FakeOrganizationProfileRepository:

    def __init__(
        self,
        profile: OrganizationProfile,
    ):
        self.profile = profile

    def get_public(
        self,
        organization_id: str,
    ) -> OrganizationProfile | None:
        if organization_id != self.profile.organization_id:
            return None

        if self.profile.status != OrganizationStatus.VERIFIED:
            return None

        return self.profile


class OrphanagePublicProfileRouteTests(unittest.TestCase):

    def setUp(self):
        self.repository = FakeOrganizationProfileRepository(
            make_profile()
        )
        self.service = OrganizationProfileService(
            self.repository
        )

        app.dependency_overrides[
            get_organization_profile_service
        ] = lambda: self.service

        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_verified_orphanage_public_profile_is_returned(self):
        response = self.client.get(
            "/orphanages/org-53/public-profile"
        )

        self.assertEqual(response.status_code, 200)

        body = response.json()

        self.assertEqual(
            body["organization_id"],
            "org-53",
        )
        self.assertEqual(
            body["organization_name"],
            "Hope Orphanage",
        )
        self.assertEqual(
            body["organization_type"],
            "orphanage",
        )
        self.assertEqual(
            body["verification_status"],
            "verified",
        )
        self.assertIn("description", body)
        self.assertIn("location", body)
        self.assertIn("contact", body)

    def test_private_information_is_not_exposed(self):
        response = self.client.get(
            "/orphanages/org-53/public-profile"
        )

        self.assertEqual(response.status_code, 200)

        body = response.json()

        self.assertNotIn("license_number", body)
        self.assertNotIn("license_expiry_date", body)
        self.assertNotIn("submitted_by", body)
        self.assertNotIn("status", body)
        self.assertNotIn("child_records", body)
        self.assertNotIn("staff_records", body)

    def test_daycare_is_rejected_by_orphanage_endpoint(self):
        self.repository.profile = make_profile(
            organization_type="daycare"
        )

        response = self.client.get(
            "/orphanages/org-53/public-profile"
        )

        self.assertEqual(response.status_code, 404)

    def test_pending_orphanage_is_not_public(self):
        self.repository.profile = make_profile(
            status=OrganizationStatus.PENDING
        )

        response = self.client.get(
            "/orphanages/org-53/public-profile"
        )

        self.assertEqual(response.status_code, 404)

    def test_unknown_orphanage_returns_not_found(self):
        response = self.client.get(
            "/orphanages/missing-org/public-profile"
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()