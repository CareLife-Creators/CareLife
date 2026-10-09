
import unittest
from datetime import datetime, timezone
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.application.use_cases.caregivers import CaregiverService
from app.domain.entities.caregiver import (
    CaregiverProfile,
    CaregiverPublicProfile,
    CaregiverType,
    CaregiverVerificationStatus,
)
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import (
    get_current_user,
)
from app.presentation.api.dependencies.caregiver import (
    get_caregiver_service,
)
from main import app


class CaregiverRouteTests(unittest.TestCase):

    def setUp(self):
        self.service = Mock(spec=CaregiverService)

        app.dependency_overrides[get_caregiver_service] = (
            lambda: self.service
        )

        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def make_profile(self):
        now = datetime.now(timezone.utc)

        return CaregiverProfile(
            user_id="caregiver-1",
            full_name="Caregiver Test",
            phone=None,
            service_type=CaregiverType.NANNY,
            bio="Experienced caregiver",
            experience_years=3,
            location="Dhaka",
            verification_status=CaregiverVerificationStatus.PENDING,
            review_message=None,
            reviewed_at=None,
            created_at=now,
            updated_at=now,
            documents=[],
        )

    def test_non_caregiver_cannot_create_profile(self):
        app.dependency_overrides[get_current_user] = lambda: (
            UserContext(
                user_id="parent-1",
                role=Role.PARENT_GUARDIAN,
            )
        )

        response = self.client.post(
            "/caregivers/me/profile",
            json={
                "service_type": "nanny",
                "experience_years": 2,
                "location": "Dhaka",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.service.create_profile.assert_not_called()

    def test_caregiver_can_create_profile(self):
        app.dependency_overrides[get_current_user] = lambda: (
            UserContext(
                user_id="caregiver-1",
                role=Role.INDEPENDENT_CAREGIVER,
            )
        )

        self.service.create_profile.return_value = self.make_profile()

        response = self.client.post(
            "/caregivers/me/profile",
            json={
                "service_type": "nanny",
                "experience_years": 3,
                "location": "Dhaka",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json()["verification_status"],
            "pending",
        )

    def test_pending_queue_requires_admin(self):
        app.dependency_overrides[get_current_user] = lambda: (
            UserContext(
                user_id="caregiver-1",
                role=Role.INDEPENDENT_CAREGIVER,
            )
        )

        response = self.client.get("/caregivers/verification/pending")

        self.assertEqual(response.status_code, 403)
        self.service.list_pending_profiles.assert_not_called()

    def test_public_response_does_not_expose_document_references(self):
        self.service.list_public_profiles.return_value = [
            CaregiverPublicProfile(
                caregiver_id="caregiver-1",
                full_name="Approved Caregiver",
                service_type=CaregiverType.NANNY,
                bio="Experienced caregiver",
                experience_years=3,
                location="Dhaka",
            )
        ]

        response = self.client.get("/caregivers")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(
            response.json()[0]["caregiver_id"],
            "caregiver-1",
        )
        self.assertNotIn(
            "document_reference",
            response.json()[0],
        )


if __name__ == "__main__":
    unittest.main()