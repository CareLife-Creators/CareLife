from app.domain.entities.organization import (
    DaycareDirectoryEntry,
    Organization,
    OrganizationStatus,
)
from app.infrastructure.database.connection import get_connection


class PostgresOrganizationRepository:

    def create(
        self,
        organization: Organization,
    ) -> Organization:

        with get_connection() as connection:
            with connection.transaction():

                connection.execute(
                    """
                    INSERT INTO organizations (
                        id,
                        name,
                        organization_type,
                        status_id,
                        submitted_by,
                        created_at,
                        updated_at,
                        updated_by
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        (
                            SELECT id
                            FROM verification_statuses
                            WHERE name = %s
                        ),
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        organization.organization_id,
                        organization.organization_name,
                        organization.organization_type,
                        organization.status.value,
                        organization.submitted_by,
                        organization.submitted_at,
                        organization.updated_at,
                        organization.submitted_by,
                    ),
                )

                connection.execute(
                    """
                    INSERT INTO organization_documents (
                        id,
                        organization_id,
                        document_type,
                        document_number,
                        expires_at,
                        created_at,
                        updated_at,
                        updated_by
                    )
                    VALUES (
                        gen_random_uuid()::text,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        organization.organization_id,
                        "license",
                        organization.license_number,
                        organization.license_expiry_date,
                        organization.submitted_at,
                        organization.updated_at,
                        organization.submitted_by,
                    ),
                )

                connection.execute(
                    """
                    INSERT INTO verification_reviews (
                        id,
                        organization_id,
                        reviewer_id,
                        status_id,
                        notes,
                        reviewed_at
                    )
                    VALUES (
                        gen_random_uuid()::text,
                        %s,
                        NULL,
                        (
                            SELECT id
                            FROM verification_statuses
                            WHERE name = %s
                        ),
                        %s,
                        %s
                    )
                    """,
                    (
                        organization.organization_id,
                        OrganizationStatus.PENDING.value,
                        "Registration submitted for verification.",
                        organization.submitted_at,
                    ),
                )

        return organization

    def get_by_organization_id(
        self,
        organization_id: str,
    ) -> Organization | None:

        with get_connection() as connection:

            row = connection.execute(
                """
                SELECT
                    o.id,
                    o.name,
                    o.organization_type,
                    document.document_number,
                    document.expires_at,
                    o.submitted_by,
                    status.name,
                    o.created_at,
                    o.updated_at,
                    latest_review.notes
                FROM organizations o

                JOIN verification_statuses status
                    ON status.id = o.status_id

                LEFT JOIN LATERAL (
                    SELECT
                        od.document_number,
                        od.expires_at
                    FROM organization_documents od
                    WHERE od.organization_id = o.id
                      AND od.document_type = 'license'
                    ORDER BY od.created_at DESC
                    LIMIT 1
                ) document
                    ON TRUE

                LEFT JOIN LATERAL (
                    SELECT
                        vr.notes
                    FROM verification_reviews vr
                    WHERE vr.organization_id = o.id
                    ORDER BY
                        vr.reviewed_at DESC,
                        vr.id DESC
                    LIMIT 1
                ) latest_review
                    ON TRUE

                WHERE o.id = %s
                """,
                (organization_id,),
            ).fetchone()

        return self._to_entity(row)

    def get_pending(
        self,
    ) -> list[Organization]:

        with get_connection() as connection:

            rows = connection.execute(
                """
                SELECT
                    o.id,
                    o.name,
                    o.organization_type,
                    document.document_number,
                    document.expires_at,
                    o.submitted_by,
                    status.name,
                    o.created_at,
                    o.updated_at,
                    latest_review.notes
                FROM organizations o

                JOIN verification_statuses status
                    ON status.id = o.status_id

                LEFT JOIN LATERAL (
                    SELECT
                        od.document_number,
                        od.expires_at
                    FROM organization_documents od
                    WHERE od.organization_id = o.id
                      AND od.document_type = 'license'
                    ORDER BY od.created_at DESC
                    LIMIT 1
                ) document
                    ON TRUE

                LEFT JOIN LATERAL (
                    SELECT
                        vr.notes
                    FROM verification_reviews vr
                    WHERE vr.organization_id = o.id
                    ORDER BY
                        vr.reviewed_at DESC,
                        vr.id DESC
                    LIMIT 1
                ) latest_review
                    ON TRUE

                WHERE status.name = %s

                ORDER BY o.created_at ASC
                """,
                (OrganizationStatus.PENDING.value,),
            ).fetchall()

        return [
            self._to_entity(row)
            for row in rows
            if row is not None
        ]

    def approve(
        self,
        organization_id: str,
        reviewer_id: str,
    ) -> Organization | None:

        with get_connection() as connection:

            with connection.transaction():

                connection.execute(
                    """
                    UPDATE organizations
                    SET
                        status_id = (
                            SELECT id
                            FROM verification_statuses
                            WHERE name = %s
                        ),
                        updated_at = CURRENT_TIMESTAMP,
                        updated_by = %s
                    WHERE id = %s
                    """,
                    (
                        OrganizationStatus.VERIFIED.value,
                        reviewer_id,
                        organization_id,
                    ),
                )

                connection.execute(
                    """
                    INSERT INTO verification_reviews (
                        id,
                        organization_id,
                        reviewer_id,
                        status_id,
                        notes,
                        reviewed_at
                    )
                    VALUES (
                        gen_random_uuid()::text,
                        %s,
                        %s,
                        (
                            SELECT id
                            FROM verification_statuses
                            WHERE name = %s
                        ),
                        NULL,
                        CURRENT_TIMESTAMP
                    )
                    """,
                    (
                        organization_id,
                        reviewer_id,
                        OrganizationStatus.VERIFIED.value,
                    ),
                )

        return self.get_by_organization_id(
            organization_id
        )

    def reject(
        self,
        organization_id: str,
        reviewer_id: str,
        message: str | None = None,
    ) -> Organization | None:

        with get_connection() as connection:

            with connection.transaction():

                connection.execute(
                    """
                    UPDATE organizations
                    SET
                        status_id = (
                            SELECT id
                            FROM verification_statuses
                            WHERE name = %s
                        ),
                        updated_at = CURRENT_TIMESTAMP,
                        updated_by = %s
                    WHERE id = %s
                    """,
                    (
                        OrganizationStatus.REJECTED.value,
                        reviewer_id,
                        organization_id,
                    ),
                )

                connection.execute(
                    """
                    INSERT INTO verification_reviews (
                        id,
                        organization_id,
                        reviewer_id,
                        status_id,
                        notes,
                        reviewed_at
                    )
                    VALUES (
                        gen_random_uuid()::text,
                        %s,
                        %s,
                        (
                            SELECT id
                            FROM verification_statuses
                            WHERE name = %s
                        ),
                        %s,
                        CURRENT_TIMESTAMP
                    )
                    """,
                    (
                        organization_id,
                        reviewer_id,
                        OrganizationStatus.REJECTED.value,
                        message,
                    ),
                )

        return self.get_by_organization_id(
            organization_id
        )

    @staticmethod
    def _to_entity(
        row,
    ) -> Organization | None:

        if row is None:
            return None

        return Organization(
            organization_id=row[0],
            organization_name=row[1],
            organization_type=row[2],
            license_number=row[3] or "",
            license_expiry_date=row[4],
            submitted_by=row[5],
            status=OrganizationStatus(row[6]),
            submitted_at=row[7],
            updated_at=row[8],
            message=row[9],
        )
            def get_daycare_directory(
        self,
        search: str | None = None,
        location: str | None = None,
    ) -> list[DaycareDirectoryEntry]:

        search_pattern = (
            f"%{search}%"
            if search is not None
            else None
        )

        location_pattern = (
            f"%{location}%"
            if location is not None
            else None
        )

        with get_connection() as connection:

            rows = connection.execute(
                """
                SELECT
                    o.id,
                    o.name,
                    o.organization_type,
                    o.description,
                    o.location,
                    o.contact

                FROM organizations o

                JOIN verification_statuses status
                    ON status.id = o.status_id

                JOIN LATERAL (
                    SELECT
                        od.expires_at
                    FROM organization_documents od
                    WHERE od.organization_id = o.id
                      AND od.document_type = 'license'
                    ORDER BY od.created_at DESC
                    LIMIT 1
                ) license
                    ON TRUE

                WHERE o.organization_type = 'daycare'

                  AND status.name = %s

                  AND license.expires_at >= CURRENT_DATE

                  AND (
                      %s IS NULL
                      OR o.name ILIKE %s
                      OR COALESCE(o.location, '') ILIKE %s
                      OR COALESCE(o.description, '') ILIKE %s
                  )

                  AND (
                      %s IS NULL
                      OR COALESCE(o.location, '') ILIKE %s
                  )

                ORDER BY o.name ASC
                """,
                (
                    OrganizationStatus.VERIFIED.value,
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    location_pattern,
                    location_pattern,
                ),
            ).fetchall()

        return [
            self._to_daycare_directory_entry(row)
            for row in rows
            if row is not None
        ]

    def get_public_daycare(
        self,
        organization_id: str,
    ) -> DaycareDirectoryEntry | None:

        with get_connection() as connection:

            row = connection.execute(
                """
                SELECT
                    o.id,
                    o.name,
                    o.organization_type,
                    o.description,
                    o.location,
                    o.contact

                FROM organizations o

                JOIN verification_statuses status
                    ON status.id = o.status_id

                JOIN LATERAL (
                    SELECT
                        od.expires_at
                    FROM organization_documents od
                    WHERE od.organization_id = o.id
                      AND od.document_type = 'license'
                    ORDER BY od.created_at DESC
                    LIMIT 1
                ) license
                    ON TRUE

                WHERE o.id = %s
                  AND o.organization_type = 'daycare'
                  AND status.name = %s
                  AND license.expires_at >= CURRENT_DATE
                """,
                (
                    organization_id,
                    OrganizationStatus.VERIFIED.value,
                ),
            ).fetchone()

        return self._to_daycare_directory_entry(row)

    @staticmethod
    def _to_daycare_directory_entry(
        row,
    ) -> DaycareDirectoryEntry | None:

        if row is None:
            return None

        return DaycareDirectoryEntry(
            organization_id=row[0],
            organization_name=row[1],
            organization_type=row[2],
            description=row[3],
            location=row[4],
            contact=row[5],
        )