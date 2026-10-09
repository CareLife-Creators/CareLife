
import unittest
from uuid import uuid4

from app.infrastructure.database.connection import get_connection
from app.infrastructure.repositories.organization_repository import (
    PostgresOrganizationRepository,
)


class LicenseExpiryDatabaseTests(unittest.TestCase):

    def setUp(self):
        self.repository = PostgresOrganizationRepository()
        self.user_id = str(uuid4())
        self.expired_id = str(uuid4())
        self.expiring_id = str(uuid4())

        with get_connection() as connection:
            with connection.transaction():
                role = connection.execute(
                    "SELECT id FROM roles WHERE name = 'parent_guardian'"
                ).fetchone()
                verified = connection.execute(
                    "SELECT id FROM verification_statuses "
                    "WHERE name = 'verified'"
                ).fetchone()

                if role is None or verified is None:
                    self.fail("Required seeded role or status is missing.")

                connection.execute(
                    """
                    INSERT INTO users (
                        id, role_id, email, password_hash,
                        full_name, is_active, created_at, updated_at
                    )
                    VALUES (
                        %s, %s, %s, 'test-only-hash',
                        'CAR-41 Test User', TRUE, NOW(), NOW()
                    )
                    """,
                    (
                        self.user_id,
                        role[0],
                        f"car41-{self.user_id}@example.test",
                    ),
                )

                for organization_id, name in (
                    (self.expired_id, "CAR-41 Expired Test"),
                    (self.expiring_id, "CAR-41 Expiring Test"),
                ):
                    connection.execute(
                        """
                        INSERT INTO organizations (
                            id, name, organization_type, status_id,
                            submitted_by, capacity, created_at, updated_at
                        )
                        VALUES (%s, %s, 'daycare', %s, %s, 20, NOW(), NOW())
                        """,
                        (
                            organization_id,
                            name,
                            verified[0],
                            self.user_id,
                        ),
                    )

                connection.execute(
                    """
                    INSERT INTO organization_documents (
                        id, organization_id, document_type,
                        document_number, expires_at,
                        created_at, updated_at, updated_by
                    )
                    VALUES (
                        %s, %s, 'license', 'CAR41-EXPIRED',
                        CURRENT_DATE - 2, NOW(), NOW(), %s
                    )
                    """,
                    (str(uuid4()), self.expired_id, self.user_id),
                )

                connection.execute(
                    """
                    INSERT INTO organization_documents (
                        id, organization_id, document_type,
                        document_number, expires_at,
                        created_at, updated_at, updated_by
                    )
                    VALUES (
                        %s, %s, 'license', 'CAR41-EXPIRING',
                        CURRENT_DATE + 10, NOW(), NOW(), %s
                    )
                    """,
                    (str(uuid4()), self.expiring_id, self.user_id),
                )

    def tearDown(self):
        with get_connection() as connection:
            with connection.transaction():
                ids = (self.expired_id, self.expiring_id)

                connection.execute(
                    """
                    DELETE FROM notifications
                    WHERE organization_id IN (%s, %s) OR user_id = %s
                    """,
                    (*ids, self.user_id),
                )
                connection.execute(
                    "DELETE FROM verification_reviews "
                    "WHERE organization_id IN (%s, %s)",
                    ids,
                )
                connection.execute(
                    "DELETE FROM organization_documents "
                    "WHERE organization_id IN (%s, %s)",
                    ids,
                )
                connection.execute(
                    "DELETE FROM user_organizations "
                    "WHERE organization_id IN (%s, %s)",
                    ids,
                )
                connection.execute(
                    "DELETE FROM organizations WHERE id IN (%s, %s)",
                    ids,
                )
                connection.execute(
                    "DELETE FROM users WHERE id = %s",
                    (self.user_id,),
                )

    def test_expired_license_updates_status_and_hides_listing(self):
        self.repository.expire_verified_organizations()

        with get_connection() as connection:
            status_row = connection.execute(
                """
                SELECT status.name
                FROM organizations o
                JOIN verification_statuses status
                    ON status.id = o.status_id
                WHERE o.id = %s
                """,
                (self.expired_id,),
            ).fetchone()

            review_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM verification_reviews r
                JOIN verification_statuses status
                    ON status.id = r.status_id
                WHERE r.organization_id = %s
                  AND status.name = 'expired'
                """,
                (self.expired_id,),
            ).fetchone()[0]

        self.assertEqual(status_row[0], "expired")
        self.assertGreaterEqual(review_count, 1)
        self.assertIsNone(
            self.repository.get_public_daycare(self.expired_id)
        )

    def test_expiry_reminder_is_not_duplicated(self):
        self.repository.create_license_expiry_reminders(30)
        self.repository.create_license_expiry_reminders(30)

        with get_connection() as connection:
            count = connection.execute(
                """
                SELECT COUNT(*)
                FROM notifications
                WHERE organization_id = %s
                  AND user_id = %s
                  AND notification_type = 'organization_license_expiry'
                """,
                (self.expiring_id, self.user_id),
            ).fetchone()[0]

        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()