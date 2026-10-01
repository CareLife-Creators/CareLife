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