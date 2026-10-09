import unittest
from datetime import date, datetime, timedelta, timezone
from unittest.mock import Mock

from app.application.use_cases.organization_verification import (
    OrganizationVerificationService,
)
from app.domain.entities.organization import Organization, OrganizationStatus


def make_organization(
    status: OrganizationStatus = OrganizationStatus.PENDING,
    license_expiry_date: date | None = None,
) -> Organization:
    now = datetime.now(timezone.utc)
    return Organization(
        organization_id="organization-1",
        organization_name="Test Daycare",
        organization_type="daycare",
        license_number="LIC-TEST-001",
        license_expiry_date=(
            license_expiry_date
            if license_expiry_date is not None
            else date.today() + timedelta(days=30)
        ),
        submitted_by="staff-1",
        status=status,
        submitted_at=now,
        updated_at=now,
    )


class OrganizationVerificationServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = Mock()
        self.service = OrganizationVerificationService(self.repository)

    def test_expired_license_cannot_be_approved(self):
        organization = make_organization(
            license_expiry_date=date.today() - timedelta(days=1)
        )
        self.repository.get_by_organization_id.return_value = organization

        with self.assertRaisesRegex(ValueError, "expired licenses"):
            self.service.approve("organization-1", "admin-1")

        self.repository.approve.assert_not_called()

    def test_non_pending_organization_cannot_be_approved(self):
        self.repository.get_by_organization_id.return_value = make_organization(
            status=OrganizationStatus.VERIFIED
        )

        with self.assertRaisesRegex(ValueError, "Only pending"):
            self.service.approve("organization-1", "admin-1")

        self.repository.approve.assert_not_called()

    def test_pending_organization_with_valid_license_can_be_approved(self):
        organization = make_organization()
        approved = make_organization(status=OrganizationStatus.VERIFIED)
        self.repository.get_by_organization_id.return_value = organization
        self.repository.approve.return_value = approved

        result = self.service.approve("organization-1", "admin-1")

        self.assertEqual(result.status, OrganizationStatus.VERIFIED)
        self.repository.approve.assert_called_once_with(
            "organization-1",
            "admin-1",
        )

    def test_approval_reports_stale_database_transition(self):
        self.repository.get_by_organization_id.return_value = make_organization()
        self.repository.approve.return_value = None

        with self.assertRaisesRegex(ValueError, "status or license eligibility"):
            self.service.approve("organization-1", "admin-1")

    def test_rejection_does_not_continue_after_a_stale_transition(self):
        self.repository.get_by_organization_id.return_value = make_organization()
        self.repository.reject.return_value = None

        with self.assertRaisesRegex(ValueError, "no longer pending"):
            self.service.reject(
                "organization-1",
                "admin-1",
                "Incomplete documents",
            )


if __name__ == "__main__":
    unittest.main()
