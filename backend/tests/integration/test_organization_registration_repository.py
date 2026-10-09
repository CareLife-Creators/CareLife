import unittest
from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

from app.domain.entities.organization import Organization, OrganizationStatus
from app.infrastructure.database.connection import get_connection
from app.infrastructure.repositories.organization_repository import PostgresOrganizationRepository


class OrganizationRegistrationRepositoryIntegrationTests(unittest.TestCase):
    def test_registration_persists_profile_and_links_submitter(self):
        user_id = str(uuid4())
        organization_id = str(uuid4())
        email = f"{user_id}@carelife.test"
        repository = PostgresOrganizationRepository()
        organization_created = False

        with get_connection() as connection:
            with connection.transaction():
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
                    (
                        user_id,
                        "daycare_staff",
                        email,
                        "test-password-hash",
                    ),
                )

        try:
            now = datetime.now(timezone.utc)
            organization = Organization(
                organization_id=organization_id,
                organization_name="Audit Test Daycare",
                organization_type="daycare",
                description="A test daycare profile",
                location="Dhaka",
                contact="+8801700000000",
                license_number=f"LIC-{organization_id[:8]}",
                license_expiry_date=date.today() + timedelta(days=30),
                submitted_by=user_id,
                status=OrganizationStatus.PENDING,
                submitted_at=now,
                updated_at=now,
            )

            repository.create(organization)
            organization_created = True

            saved = repository.get_by_organization_id(organization_id)
            self.assertIsNotNone(saved)
            self.assertEqual(saved.description, "A test daycare profile")
            self.assertEqual(saved.location, "Dhaka")
            self.assertEqual(saved.contact, "+8801700000000")

            with get_connection() as connection:
                membership = connection.execute(
                    """
                    SELECT 1
                    FROM user_organizations
                    WHERE user_id = %s AND organization_id = %s
                    """,
                    (user_id, organization_id),
                ).fetchone()

            self.assertIsNotNone(membership)
        finally:
            with get_connection() as connection:
                with connection.transaction():
                    if organization_created:
                        connection.execute(
                            "DELETE FROM organizations WHERE id = %s",
                            (organization_id,),
                        )
                    connection.execute(
                        "DELETE FROM users WHERE id = %s",
                        (user_id,),
                    )


if __name__ == "__main__":
    unittest.main()
