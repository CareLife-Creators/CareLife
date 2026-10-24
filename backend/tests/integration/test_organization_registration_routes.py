import unittest
from datetime import date, timedelta
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.application.use_cases.organization_registration import (
    OrganizationRegistrationService,
)
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import (
    get_current_user,
)
from app.presentation.api.dependencies.organization import (
    get_organization_registration_service,
)
from main import app


class OrganizationRegistrationRouteTests(unittest.TestCase):

    def setUp(self):
        self.service = Mock(spec=OrganizationRegistrationService)

        self.service.register.side_effect = (
            lambda request, submitted_by: {
                "organization_id": "registration-1",
                "organization_name": request.organization_name,
                "organization_type": request.organization_type,
                "license_number": request.license_number,
                "license_expiry_date": (
                    request.license_expiry_date.isoformat()
                ),
                "submitted_by": submitted_by,
                "status": "pending",
                "submitted_at": "2026-10-03T00:00:00+00:00",
            }
        )

        app.dependency_overrides[
            get_organization_registration_service
        ] = lambda: self.service

        self.client = TestClient(app)

        self.valid_payload = {
            "organization_name": "Sunshine Daycare Center",
            "organization_type": "daycare",
            "license_number": "LIC-2026-001",
            "license_expiry_date": (
                date.today() + timedelta(days=30)
            ).isoformat(),
        }

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_unauthenticated_user_is_rejected(self):
        response = self.client.post(
            "/organizations/register",
            json=self.valid_payload,
        )

        self.assertEqual(response.status_code, 401)
        self.service.register.assert_not_called()

    def test_authenticated_member_can_submit_registration_for_review(self):
        member = UserContext(
            user_id="member-1",
            role=Role.PARENT_GUARDIAN,
        )

        app.dependency_overrides[get_current_user] = (
            lambda: member
        )

        response = self.client.post(
            "/organizations/register",
            json=self.valid_payload,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()["status"],
            "pending",
        )
        self.assertEqual(
            response.json()["submitted_by"],
            "member-1",
        )
        self.assertEqual(
            response.json()["organization_type"],
            "daycare",
        )

        self.service.register.assert_called_once()

    def test_member_can_apply_for_any_organization_type(self):
        member = UserContext(
            user_id="member-1",
            role=Role.PARENT_GUARDIAN,
        )

        app.dependency_overrides[get_current_user] = (
            lambda: member
        )

        mismatched_payload = {
            **self.valid_payload,
            "organization_name": "Test Orphanage",
            "organization_type": "orphanage",
        }

        response = self.client.post(
            "/organizations/register",
            json=mismatched_payload,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["organization_type"], "orphanage")
        self.service.register.assert_called_once()

    def test_invalid_payload_is_rejected(self):
        member = UserContext(
            user_id="member-1",
            role=Role.PARENT_GUARDIAN,
        )

        app.dependency_overrides[get_current_user] = (
            lambda: member
        )

        invalid_payload = {
            **self.valid_payload,
            "organization_name": "",
        }

        response = self.client.post(
            "/organizations/register",
            json=invalid_payload,
        )

        self.assertEqual(response.status_code, 422)
        self.service.register.assert_not_called()

    def test_administrator_cannot_submit_organization_application(self):
        admin = UserContext(
            user_id="admin-1",
            role=Role.CARELIFE_ADMIN,
            organization_id=None,
        )

        app.dependency_overrides[get_current_user] = (
            lambda: admin
        )

        response = self.client.post(
            "/organizations/register",
            json=self.valid_payload,
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "Administrator accounts cannot submit organization applications")
        self.service.register.assert_not_called()


if __name__ == "__main__":
    unittest.main()
