import unittest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock

from app.application.schemas.in_kind_donation import (
    InKindDonationPledgeCreateRequest,
    InKindDonationStatusUpdateRequest,
)
from app.application.use_cases.in_kind_donations import (
    InKindDonationService,
)
from app.domain.entities.in_kind_donation import (
    InKindDonationPledge,
    InKindDonationStatus,
)
from app.domain.entities.user_context import Role, UserContext


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


class InKindDonationServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = Mock()
        self.repository.is_authorized_organization_staff.return_value = True

        self.service = InKindDonationService(self.repository)

        self.donor = UserContext(
            user_id="donor-1",
            role=Role.DONOR_SUPPORTER,
        )

        self.staff = UserContext(
            user_id="staff-1",
            role=Role.CARE_HOME_STAFF,
            organization_id="org-1",
            organization_ids=["org-1"],
        )

    def test_donor_can_submit_a_pledge(self):
        self.repository.create_pledge.side_effect = (
            lambda pledge, donor_id: pledge.model_copy(
                update={
                    "need_title": "Rice",
                    "organization_id": "org-1",
                    "organization_name": "Sunrise Care",
                    "unit": "kg",
                }
            )
        )

        request = InKindDonationPledgeCreateRequest(
            quantity=Decimal("10.000"),
            notes="Rice donation",
        )

        result = self.service.create_pledge(
            self.donor,
            "need-1",
            request,
        )

        self.assertEqual(result.need_id, "need-1")
        self.assertEqual(result.donor_id, "donor-1")
        self.assertEqual(result.quantity, Decimal("10.000"))
        self.assertEqual(
            result.status,
            InKindDonationStatus.PLEDGED,
        )
        self.repository.create_pledge.assert_called_once()

    def test_non_donor_cannot_submit_a_pledge(self):
        parent = UserContext(
            user_id="parent-1",
            role=Role.PARENT_GUARDIAN,
        )

        request = InKindDonationPledgeCreateRequest(
            quantity=Decimal("2.000"),
        )

        with self.assertRaises(PermissionError):
            self.service.create_pledge(
                parent,
                "need-1",
                request,
            )

        self.repository.create_pledge.assert_not_called()

    def test_donor_can_only_list_their_own_pledges(self):
        pledge = make_pledge()
        self.repository.list_pledges_for_donor.return_value = [pledge]

        result = self.service.list_my_pledges(self.donor)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].donor_id, "donor-1")
        self.repository.list_pledges_for_donor.assert_called_once_with(
            "donor-1"
        )

    def test_staff_can_list_organization_pledges(self):
        pledge = make_pledge()
        self.repository.list_pledges_for_organization.return_value = [
            pledge
        ]

        result = self.service.list_organization_pledges(
            self.staff,
            "org-1",
        )

        self.assertEqual(len(result), 1)
        self.repository.is_authorized_organization_staff.assert_called_once_with(
            "org-1",
            "staff-1",
            Role.CARE_HOME_STAFF,
        )

    def test_staff_cannot_manage_another_organization(self):
        with self.assertRaises(PermissionError):
            self.service.list_organization_pledges(
                self.staff,
                "org-2",
            )

        self.repository.list_pledges_for_organization.assert_not_called()

    def test_pledge_can_move_from_pledged_to_received(self):
        pledged = make_pledge(InKindDonationStatus.PLEDGED)
        received = make_pledge(InKindDonationStatus.RECEIVED)

        self.repository.get_pledge_for_organization.return_value = pledged
        self.repository.transition_pledge_status.return_value = received

        result = self.service.update_pledge_status(
            self.staff,
            "org-1",
            "pledge-1",
            InKindDonationStatusUpdateRequest(status="received"),
        )

        self.assertEqual(
            result.status,
            InKindDonationStatus.RECEIVED,
        )
        self.repository.transition_pledge_status.assert_called_once()

    def test_pledge_cannot_skip_directly_to_allocated(self):
        pledged = make_pledge(InKindDonationStatus.PLEDGED)
        self.repository.get_pledge_for_organization.return_value = pledged

        with self.assertRaises(ValueError):
            self.service.update_pledge_status(
                self.staff,
                "org-1",
                "pledge-1",
                InKindDonationStatusUpdateRequest(status="allocated"),
            )

        self.repository.transition_pledge_status.assert_not_called()

    def test_missing_pledge_returns_not_found(self):
        self.repository.get_pledge_for_organization.return_value = None

        with self.assertRaises(LookupError):
            self.service.update_pledge_status(
                self.staff,
                "org-1",
                "missing-pledge",
                InKindDonationStatusUpdateRequest(status="received"),
            )


if __name__ == "__main__":
    unittest.main()