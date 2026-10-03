from app.domain.entities.organization_verification import (
    OrganizationVerification,
    VerificationStatus,
)
from app.infrastructure.database.connection import get_connection


class PostgresOrganizationVerificationRepository:
    def get_by_organization_id(
        self,
        organization_id: str,
    ) -> OrganizationVerification | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    organization_id,
                    organization_name,
                    organization_type,
                    status,
                    submitted_at,
                    updated_at,
                    message
                FROM organization_verifications
                WHERE organization_id = %s
                """,
                (organization_id,),
            ).fetchone()

        return self._to_entity(row)

    def get_pending(
        self,
    ) -> list[OrganizationVerification]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    organization_id,
                    organization_name,
                    organization_type,
                    status,
                    submitted_at,
                    updated_at,
                    message
                FROM organization_verifications
                WHERE status = 'pending'
                ORDER BY submitted_at ASC
                """
            ).fetchall()

        return [
            self._to_entity(row)
            for row in rows
            if row is not None
        ]

    def approve(
        self,
        organization_id: str,
    ) -> OrganizationVerification | None:
        with get_connection() as connection:
            with connection.transaction():
                connection.execute(
                    """
                    UPDATE organization_verifications
                    SET
                        status = 'approved',
                        updated_at = CURRENT_TIMESTAMP,
                        message = NULL
                    WHERE organization_id = %s
                    """,
                    (organization_id,),
                )

        return self.get_by_organization_id(organization_id)

    def reject(
        self,
        organization_id: str,
        message: str | None = None,
    ) -> OrganizationVerification | None:
        with get_connection() as connection:
            with connection.transaction():
                connection.execute(
                    """
                    UPDATE organization_verifications
                    SET
                        status = 'rejected',
                        updated_at = CURRENT_TIMESTAMP,
                        message = %s
                    WHERE organization_id = %s
                    """,
                    (message, organization_id),
                )

        return self.get_by_organization_id(organization_id)

    @staticmethod
    def _to_entity(row) -> OrganizationVerification | None:
        if row is None:
            return None

        return OrganizationVerification(
            organization_id=row[0],
            organization_name=row[1],
            organization_type=row[2],
            status=VerificationStatus(row[3]),
            submitted_at=row[4],
            updated_at=row[5],
            message=row[6],
        )