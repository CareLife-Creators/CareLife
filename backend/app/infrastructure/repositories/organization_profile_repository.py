from app.domain.entities.organization import OrganizationStatus
from app.domain.entities.organization_profile import (
    OrganizationProfile,
)
from app.infrastructure.database.connection import get_connection


class PostgresOrganizationProfileRepository:

    UPDATE_COLUMNS = {
        "organization_name": "name",
        "description": "description",
        "location": "location",
        "contact": "contact",
        "capacity": "capacity",
        "age_range": "age_range",
        "opening_hours": "opening_hours",
        "facilities": "facilities",
        "fees": "fees",
    }

    def get_for_staff(
        self,
        organization_id: str,
    ) -> OrganizationProfile | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    o.id,
                    o.name,
                    o.organization_type,
                    o.description,
                    o.location,
                    o.contact,
                    o.capacity,
                    o.age_range,
                    o.opening_hours,
                    o.facilities,
                    o.fees,
                    status.name,
                    o.updated_at
                FROM organizations o
                JOIN verification_statuses status
                    ON status.id = o.status_id
                WHERE o.id = %s
                """,
                (organization_id,),
            ).fetchone()

        return self._to_profile(row)

    def get_public(
        self,
        organization_id: str,
    ) -> OrganizationProfile | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    o.id,
                    o.name,
                    o.organization_type,
                    o.description,
                    o.location,
                    o.contact,
                    o.capacity,
                    o.age_range,
                    o.opening_hours,
                    o.facilities,
                    o.fees,
                    status.name,
                    o.updated_at
                FROM organizations o
                JOIN verification_statuses status
                    ON status.id = o.status_id

                JOIN LATERAL (
                    SELECT od.expires_at
                    FROM organization_documents od
                    WHERE od.organization_id = o.id
                      AND od.document_type = 'license'
                    ORDER BY od.created_at DESC, od.id DESC
                    LIMIT 1
                ) latest_license ON TRUE

                WHERE o.id = %s
                  AND status.name = %s
                  AND latest_license.expires_at >= CURRENT_DATE
                """,
                (
                    organization_id,
                    OrganizationStatus.VERIFIED.value,
                ),
            ).fetchone()

        return self._to_profile(row)

    def update_profile(
        self,
        organization_id: str,
        changes: dict[str, object],
        updated_by: str,
    ) -> OrganizationProfile | None:

        if not changes:
            raise ValueError(
                "At least one profile field must be provided."
            )

        unsupported_fields = (
            set(changes) - set(self.UPDATE_COLUMNS)
        )

        if unsupported_fields:
            raise ValueError(
                "One or more fields cannot be updated."
            )

        assignments = [
            f"{self.UPDATE_COLUMNS[field]} = %s"
            for field in changes
        ]

        values = [
            changes[field]
            for field in changes
        ]

        assignments.extend([
            "updated_at = CURRENT_TIMESTAMP",
            "updated_by = %s",
        ])

        values.append(updated_by)
        values.append(organization_id)

        with get_connection() as connection:
            with connection.transaction():
                updated_row = connection.execute(
                    f"""
                    UPDATE organizations
                    SET {", ".join(assignments)}
                    WHERE id = %s
                    RETURNING id
                    """,
                    values,
                ).fetchone()

        if updated_row is None:
            return None

        return self.get_for_staff(organization_id)

    @staticmethod
    def _to_profile(
        row,
    ) -> OrganizationProfile | None:
        if row is None:
            return None

        return OrganizationProfile(
            organization_id=row[0],
            organization_name=row[1],
            organization_type=row[2],
            description=row[3],
            location=row[4],
            contact=row[5],
            capacity=row[6],
            age_range=row[7],
            opening_hours=row[8],
            facilities=row[9],
            fees=row[10],
            status=OrganizationStatus(row[11]),
            updated_at=row[12],
        )