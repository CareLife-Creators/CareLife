import unittest
from unittest.mock import Mock

from app.application.use_cases.organization_verification import (
    OrganizationVerificationService,
)


class LicenseExpiryMonitorTests(unittest.TestCase):

    def setUp(self):
        self.repository = Mock()
        self.service = OrganizationVerificationService(
            repository=self.repository
        )

    def test_monitor_returns_correct_counts(self):
        self.repository.expire_verified_organizations.return_value = 2
        self.repository.create_license_expiry_reminders.return_value = 3

        result = self.service.monitor_license_expiry(
            reminder_days=30
        )

        self.assertEqual(
            result,
            {
                "expired_organizations": 2,
                "reminders_created": 3,
                "reminder_failed": False,
            },
        )

    def test_reminder_failure_does_not_lose_expiry_result(self):
        self.repository.expire_verified_organizations.return_value = 2
        self.repository.create_license_expiry_reminders.side_effect = (
            RuntimeError("Simulated notification failure")
        )

        with self.assertLogs(
            "app.application.use_cases.organization_verification",
            level="ERROR",
        ):
            result = self.service.monitor_license_expiry(
                reminder_days=30
            )

        self.assertEqual(result["expired_organizations"], 2)
        self.assertEqual(result["reminders_created"], 0)
        self.assertTrue(result["reminder_failed"])


if __name__ == "__main__":
    unittest.main()