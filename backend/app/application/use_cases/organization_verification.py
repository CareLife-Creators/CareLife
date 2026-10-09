import logging
from datetime import date

from app.application.interfaces.organization import (
    OrganizationRepository,
)
from app.domain.entities.organization import (
    OrganizationStatus,
)
logger = logging.getLogger(__name__)

class OrganizationVerificationService:

    def __init__(
        self,
        repository: OrganizationRepository,
    ):
        self.repository = repository

    def get_status(
        self,
        organization_id: str,
    ):
        organization = (
            self.repository.get_by_organization_id(
                organization_id
            )
        )

        if organization is None:
            raise ValueError(
                "Verification information not found"
            )

        return organization

    def get_pending(self):
        return self.repository.get_pending()

    def get_daycare_directory(
        self,
        search: str | None = None,
        location: str | None = None,
    ):
        return self.repository.get_daycare_directory(
            search=search,
            location=location,
        )

    def get_public_daycare(
        self,
        organization_id: str,
    ):
        organization = (
            self.repository.get_public_daycare(
                organization_id
            )
        )

        if organization is None:
            raise ValueError(
                "Verified daycare not found"
            )

        return organization

    def approve(
        self,
        organization_id: str,
        reviewer_id: str,
    ):
        organization = (
            self.repository.get_by_organization_id(
                organization_id
            )
        )

        if organization is None:
            raise ValueError(
                "Verification information not found"
            )

        if organization.status != OrganizationStatus.PENDING:
            raise ValueError(
                "Only pending organizations can be approved"
            )

        if organization.license_expiry_date < date.today():
            raise ValueError(
                "Organizations with expired licenses cannot be approved"
            )

        updated = self.repository.approve(
            organization_id,
            reviewer_id,
        )

        if updated is None:
            raise ValueError(
                "Organization could not be approved; its status or license eligibility may have changed"
            )

        return updated

    def reject(
        self,
        organization_id: str,
        reviewer_id: str,
        message: str | None = None,
    ):
        organization = (
            self.repository.get_by_organization_id(
                organization_id
            )
        )

        if organization is None:
            raise ValueError(
                "Verification information not found"
            )

        if organization.status != OrganizationStatus.PENDING:
            raise ValueError(
                "Only pending organizations can be rejected"
            )

        updated = self.repository.reject(
            organization_id,
            reviewer_id,
            message,
        )

        if updated is None:
            raise ValueError(
                "Organization could not be rejected because it is no longer pending"
            )

        return updated

    def monitor_license_expiry(
        self,
        reminder_days: int,
    ) -> dict[str, int | bool]:
        expired_count = (
            self.repository.expire_verified_organizations()
        )

        try:
            reminders_created = (
                self.repository.create_license_expiry_reminders(
                    reminder_days
                )
            )
        except Exception:
            logger.exception(
                "Failed to create organization license expiry reminders"
            )

            return {
                "expired_organizations": expired_count,
                "reminders_created": 0,
                "reminder_failed": True,
            }

        return {
            "expired_organizations": expired_count,
            "reminders_created": reminders_created,
            "reminder_failed": False,
        }