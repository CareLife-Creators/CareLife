import unittest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock

from app.application.schemas.donation import (
    DonationCampaignCreateRequest,
    DonationNeedUpdateRequest,
)
from app.application.use_cases.donations import DonationService
from app.domain.entities.donation import DonationCampaign, DonationNeed, DonationNeedType
from app.domain.entities.user_context import Role, UserContext


class DonationServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = Mock()
        self.repository.is_authorized_organization_staff.return_value = True
        self.service = DonationService(self.repository)
        self.staff = UserContext(
            user_id="staff-1",
            role=Role.DAYCARE_STAFF,
            organization_id="daycare-1",
            organization_ids=["daycare-1"],
        )
        self.parent = UserContext(
            user_id="parent-1",
            role=Role.PARENT_GUARDIAN,
        )
        now = datetime.now(timezone.utc)
        self.need = DonationNeed(
            id="need-1",
            organization_id="daycare-1",
            organization_name="Test Daycare",
            organization_type="daycare",
            title="Milk",
            description=None,
            category="food",
            need_type=DonationNeedType.MONETARY,
            target_amount=Decimal("100.00"),
            target_quantity=None,
            unit=None,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    def test_authorized_staff_can_create_campaign(self):
        self.repository.create_campaign.side_effect = (
            lambda campaign, user_id, role: campaign
        )
        request = DonationCampaignCreateRequest(
            title="Winter supplies",
            target_amount=Decimal("1000.00"),
        )

        result = self.service.create_campaign(
            self.staff,
            "daycare-1",
            request,
        )

        self.assertEqual(result.title, "Winter supplies")
        self.assertEqual(result.target_amount, Decimal("1000.00"))
        self.assertEqual(result.received_amount, Decimal("0.00"))
        self.repository.create_campaign.assert_called_once()

    def test_parent_cannot_create_campaign(self):
        request = DonationCampaignCreateRequest(
            title="Winter supplies",
            target_amount=Decimal("1000.00"),
        )

        with self.assertRaises(PermissionError):
            self.service.create_campaign(self.parent, "daycare-1", request)

        self.repository.create_campaign.assert_not_called()
        self.repository.is_authorized_organization_staff.assert_not_called()

    def test_staff_cannot_manage_another_organization(self):
        request = DonationCampaignCreateRequest(
            title="Winter supplies",
            target_amount=Decimal("1000.00"),
        )

        with self.assertRaises(PermissionError):
            self.service.create_campaign(self.staff, "daycare-2", request)

        self.repository.create_campaign.assert_not_called()
        self.repository.is_authorized_organization_staff.assert_not_called()

    def test_staff_without_database_membership_is_rejected(self):
        self.repository.is_authorized_organization_staff.return_value = False
        request = DonationCampaignCreateRequest(
            title="Winter supplies",
            target_amount=Decimal("1000.00"),
        )

        with self.assertRaises(PermissionError):
            self.service.create_campaign(self.staff, "daycare-1", request)

        self.repository.create_campaign.assert_not_called()

    def test_partial_update_cannot_leave_need_type_inconsistent(self):
        self.repository.get_need_for_organization.return_value = self.need
        request = DonationNeedUpdateRequest(need_type=DonationNeedType.IN_KIND)

        with self.assertRaises(ValueError):
            self.service.update_need(
                self.staff,
                "daycare-1",
                "need-1",
                request,
            )

        self.repository.update_need.assert_not_called()

    def test_public_campaign_missing_from_repository_returns_not_found(self):
        self.repository.get_public_campaign.return_value = None

        with self.assertRaisesRegex(LookupError, "Active campaign"):
            self.service.get_public_campaign("missing-campaign")


if __name__ == "__main__":
    unittest.main()
