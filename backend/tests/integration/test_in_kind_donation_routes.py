import unittest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.application.use_cases.in_kind_donations import (
    InKindDonationService,
)
from app.domain.entities.in_kind_donation import (
    InKindDonationPledge,
    InKindDonationStatus,
)
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import (
    get_current_user,
)
from app.presentation.api.dependencies.in_kind_donation import (
    get_in_kind_donation_service,
)
from main import app


def make_pledge(
    status: InKindDonationStatus = InKindDonationStatus.PLEDGED,
) -> InKindDonationPledge:
    now = datetime.now(timezone.utc)
    has_been_received = status in {
        InKindDonationStatus.RECEIVED,
        InKindDonationStatus.ALLOCATED,
    }
    has_been_allocated = status == InKindDonationStatus.ALLOCATED

    return InKindDonationPledge(
        id="pledge-1",
        need_id="need-1",
        need_title="Rice",
        organization_id="org-1",
        organization_name="Sunrise Care",
        donor_id="donor-1",
        quantity=Decimal("10.000"),
        unit="kg",
        notes="Rice donation",
        status=status,
        received_by="staff-1" if has_been_received else None,
        received_at=now if has_been_received else None,
        allocated_by="staff-1" if has_been_allocated else None,
        allocated_at=now if has_been_allocated else None,
        created_at=now,
        updated_at=now,
    )


class InKindDonationRouteTests(unittest.TestCase):
    def setUp(self):
        self.service = Mock(spec=InKindDonationService)
        self.current_user = UserContext(
            user_id="donor-1",
            role=Role.DONOR_SUPPORTER,
        )
        self.pledge = make_pledge()

        app.dependency_overrides[get_current_user] = (
            lambda: self.current_user
        )
        app.dependency_overrides[get_in_kind_donation_service] = (
            lambda: self.service
        )

        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(
            get_in_kind_donation_service,
            None,
        )

    def test_donor_can_submit_a_pledge(self):
        self.service.create_pledge.return_value = self.pledge

        response = self.client.post(
            "/donation-needs/need-1/in-kind-pledges",
            json={
                "quantity": "10.000",
                "notes": "Rice donation",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["id"], "pledge-1")
        self.assertEqual(response.json()["status"], "pledged")
        self.assertEqual(response.json()["quantity"], "10.000")
        self.service.create_pledge.assert_called_once()

    def test_donor_can_view_their_pledge_history(self):
        self.service.list_my_pledges.return_value = [self.pledge]

        response = self.client.get("/my/in-kind-pledges")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["donor_id"], "donor-1")

    def test_staff_can_mark_a_pledge_as_received(self):
        self.current_user = UserContext(
            user_id="staff-1",
            role=Role.CARE_HOME_STAFF,
            organization_id="org-1",
            organization_ids=["org-1"],
        )
        received_pledge = make_pledge(
            InKindDonationStatus.RECEIVED
        )
        self.service.update_pledge_status.return_value = received_pledge

        response = self.client.patch(
            "/organizations/org-1/in-kind-pledges/pledge-1/status",
            json={"status": "received"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "received")
        self.service.update_pledge_status.assert_called_once()

    def test_permission_error_returns_forbidden(self):
        self.service.create_pledge.side_effect = PermissionError(
            "Donor-supporter access is required"
        )

        response = self.client.post(
            "/donation-needs/need-1/in-kind-pledges",
            json={"quantity": "2.000"},
        )

        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()