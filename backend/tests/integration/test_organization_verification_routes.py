import unittest

from fastapi.testclient import TestClient

from app.application.use_cases.organization_verification import (
    OrganizationVerificationService,
)
from app.domain.entities.organization import (
    Organization,
    OrganizationStatus,
)
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import (
    get_current_user,
)
from app.presentation.api.dependencies.organization import (
    get_organization_verification_service,
)
from main import app


class FakeOrganizationRepository:

    def get_by_organization_id(
        self,
        organization_id,
    ):
        if organization_id != "daycare-1":
            return None

        return Organization(
            organization_id="daycare-1",
            organization_name="Sunshine Daycare Center",
            organization_type="daycare",
            license_number="LIC-2026-001",
            license_expiry_date="2027-01-01",
            submitted_by="staff-1",
            status=OrganizationStatus.VERIFIED,
            submitted_at="2026-09-28T06:00:00+06:00",
            updated_at="2026-10-02T00:43:46+06:00",
            message="Your organization has been verified successfully.",
        )


class OrganizationVerificationRouteTests(unittest.TestCase):

    def setUp(self):
        repository = FakeOrganizationRepository()

        self.service = OrganizationVerificationService(
            repository=repository
        )

        app.dependency_overrides[
            get_organization_verification_service
        ] = lambda: self.service

        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_unauthenticated_user_is_rejected(self):
        response = self.client.get(
            "/organizations/daycare-1/verification-status"
        )

        self.assertEqual(
            response.status_code,
            401,
        )

    def test_same_organization_can_view_status(self):
        staff_user = UserContext(
            user_id="staff-1",
            role=Role.DAYCARE_STAFF,
            organization_id="daycare-1",
        )

        app.dependency_overrides[get_current_user] = (
            lambda: staff_user
        )

        response = self.client.get(
            "/organizations/daycare-1/verification-status"
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.json()["organization_id"],
            "daycare-1",
        )

        self.assertEqual(
            response.json()["organization_name"],
            "Sunshine Daycare Center",
        )

        self.assertEqual(
            response.json()["organization_type"],
            "daycare",
        )

        self.assertEqual(
            response.json()["license_number"],
            "LIC-2026-001",
        )

        self.assertEqual(
            response.json()["submitted_by"],
            "staff-1",
        )

        self.assertEqual(
            response.json()["status"],
            "verified",
        )

    def test_different_organization_is_rejected(self):
        staff_user = UserContext(
            user_id="staff-1",
            role=Role.DAYCARE_STAFF,
            organization_id="daycare-1",
        )

        app.dependency_overrides[get_current_user] = (
            lambda: staff_user
        )

        response = self.client.get(
            "/organizations/daycare-2/verification-status"
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_missing_verification_returns_404(self):
        staff_user = UserContext(
            user_id="staff-1",
            role=Role.DAYCARE_STAFF,
            organization_id="daycare-3",
        )

        app.dependency_overrides[get_current_user] = (
            lambda: staff_user
        )

        response = self.client.get(
            "/organizations/daycare-3/verification-status"
        )

        self.assertEqual(
            response.status_code,
            404,
        )


if __name__ == "__main__":
    unittest.main()