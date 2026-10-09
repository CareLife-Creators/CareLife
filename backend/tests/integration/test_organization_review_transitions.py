import unittest
from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

from app.domain.entities.organization import Organization, OrganizationStatus
from app.infrastructure.database.connection import get_connection
from app.infrastructure.repositories.organization_repository import PostgresOrganizationRepository


class OrganizationReviewTransitionIntegrationTests(unittest.TestCase):
    def test_reviews_are_atomic_pending_only_and_license_aware(self):
        repository = PostgresOrganizationRepository()
        staff_id = str(uuid4())
        admin_id = str(uuid4())
        staff_email = f"{staff_id}@carelife.test"
        admin_email = f"{admin_id}@carelife.test"
        expired_org_id = str(uuid4())
        current_org_id = str(uuid4())
        created_org_ids: list[str] = []

        with get_connection() as connection:
            with connection.transaction():
                for user_id, role_name, email in (
                    (staff_id, "daycare_staff", staff_email),
                    (admin_id, "carelife_admin", admin_email),
                ):
                    connection.execute(
                        """
                        INSERT INTO users (
                            id, role_id, email, password_hash, is_active
                        )
                        VALUES (
                            %s,
                            (SELECT id FROM roles WHERE name = %s),
                            %s,
                            %s,
                            TRUE
                        )
                        """,
                        (user_id, role_name, email, "test-password-hash"),
                    )

        try:
            now = datetime.now(timezone.utc)
            organizations = [
                Organization(
                    organization_id=expired_org_id,
                    organization_name="Expired License Test",
                    organization_type="daycare",
                    license_number=f"LIC-{expired_org_id[:8]}",
                    license_expiry_date=date.today() - timedelta(days=1),
                    submitted_by=staff_id,
                    status=OrganizationStatus.PENDING,
                    submitted_at=now,
                    updated_at=now,
                ),
                Organization(
                    organization_id=current_org_id,
                    organization_name="Valid License Test",
                    organization_type="daycare",
                    license_number=f"LIC-{current_org_id[:8]}",
                    license_expiry_date=date.today() + timedelta(days=30),
                    submitted_by=staff_id,
                    status=OrganizationStatus.PENDING,
                    submitted_at=now,
                    updated_at=now,
                ),
            ]

            for organization in organizations:
                repository.create(organization)
                created_org_ids.append(organization.organization_id)

            expired_result = repository.approve(expired_org_id, admin_id)
            self.assertIsNone(expired_result)
            still_pending = repository.get_by_organization_id(expired_org_id)
            self.assertEqual(still_pending.status, OrganizationStatus.PENDING)

            approved = repository.approve(current_org_id, admin_id)
            self.assertIsNotNone(approved)
            self.assertEqual(approved.status, OrganizationStatus.VERIFIED)

            # A second reviewer decision must not overwrite a completed review.
            self.assertIsNone(
                repository.reject(
                    current_org_id,
                    admin_id,
                    "A later conflicting decision",
                )
            )
            self.assertIsNone(repository.approve(current_org_id, admin_id))
            saved = repository.get_by_organization_id(current_org_id)
            self.assertEqual(saved.status, OrganizationStatus.VERIFIED)
        finally:
            with get_connection() as connection:
                with connection.transaction():
                    for organization_id in created_org_ids:
                        connection.execute(
                            "DELETE FROM organizations WHERE id = %s",
                            (organization_id,),
                        )
                    connection.execute(
                        "DELETE FROM users WHERE id IN (%s, %s)",
                        (staff_id, admin_id),
                    )


if __name__ == "__main__":
    unittest.main()
