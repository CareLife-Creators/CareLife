import unittest
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.application.use_cases.organization_verification import (
    OrganizationVerificationService,
)
from app.domain.entities.organization import ElderCareDirectoryEntry
from app.presentation.api.dependencies.organization import (
    get_organization_verification_service,
)
from main import app


class ElderCareDirectoryRouteTests(unittest.TestCase):

    def setUp(self):
        self.service = Mock(
            spec=OrganizationVerificationService
        )
        app.dependency_overrides[
            get_organization_verification_service
        ] = lambda: self.service
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.pop(
            get_organization_verification_service,
            None,
        )

    def test_search_returns_matching_results(self):
        self.service.get_elder_care_directory.return_value = [
            ElderCareDirectoryEntry(
                organization_id="elder-1",
                organization_name="Sunrise Elder Care",
                organization_type="elderly_care",
                description="Residential elder care",
                location="Dhaka",
                contact="01700000000",
                capacity=35,
            )
        ]

        response = self.client.get(
            "/organizations/elder-care",
            params={
                "search": "Sunrise",
                "location": "Dhaka",
                "min_capacity": 20,
                "max_capacity": 50,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(
            response.json()[0]["organization_name"],
            "Sunrise Elder Care",
        )
        self.assertEqual(response.json()[0]["capacity"], 35)

    def test_no_matches_return_empty_list(self):
        self.service.get_elder_care_directory.return_value = []

        response = self.client.get(
            "/organizations/elder-care",
            params={"search": "NoSuchCareHome"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_invalid_capacity_range_returns_422(self):
        response = self.client.get(
            "/organizations/elder-care",
            params={
                "min_capacity": 50,
                "max_capacity": 10,
            },
        )

        self.assertEqual(response.status_code, 422)
        self.service.get_elder_care_directory.assert_not_called()

    def test_negative_capacity_returns_422(self):
        response = self.client.get(
            "/organizations/elder-care",
            params={"min_capacity": -1},
        )

        self.assertEqual(response.status_code, 422)
        self.service.get_elder_care_directory.assert_not_called()


if __name__ == "__main__":
    unittest.main()