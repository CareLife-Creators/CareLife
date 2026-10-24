from app.domain.entities.organization import (
    DaycareDirectoryEntry,
    ElderCareDirectoryEntry,
    Organization,
    OrganizationStatus,
    OrganizationReviewEvent,
    OrganizationTrackingRecord,
    OrganizationMapEntry,
)
from app.infrastructure.database.connection import get_connection
from app.infrastructure.repositories.audit_log_repository import (
    PostgresAuditLogRepository,
)


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
                        description,
                        location,
                        latitude,
                        longitude,
                        contact,
                        capacity,
                        age_range,
                        opening_hours,
                        facilities,
                        fees,
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
                        %s,
                        %s,
                        %s,
                        %s,
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
                        organization.organization_name,
                        organization.organization_type,
                        organization.status.value,
                        organization.submitted_by,
                        organization.description,
                        organization.location,
                        organization.latitude,
                        organization.longitude,
                        organization.contact,
                        organization.capacity,
                        organization.age_range,
                        organization.opening_hours,
                        organization.facilities,
                        organization.fees,
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
                    latest_review.notes,
                    o.description,
                    o.location,
                    o.latitude,
                    o.longitude,
                    o.contact
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
                ) document ON TRUE
                LEFT JOIN LATERAL (
                    SELECT vr.notes
                    FROM verification_reviews vr
                    WHERE vr.organization_id = o.id
                    ORDER BY
                        vr.reviewed_at DESC,
                        vr.id DESC
                    LIMIT 1
                ) latest_review ON TRUE
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
                    latest_review.notes,
                    o.description,
                    o.location,
                    o.contact
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
                ) document ON TRUE
                LEFT JOIN LATERAL (
                    SELECT vr.notes
                    FROM verification_reviews vr
                    WHERE vr.organization_id = o.id
                    ORDER BY
                        vr.reviewed_at DESC,
                        vr.id DESC
                    LIMIT 1
                ) latest_review ON TRUE
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

    def get_submitted_by(self, user_id: str) -> list[Organization]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT o.id, o.name, o.organization_type,
                       document.document_number, document.expires_at,
                       o.submitted_by, status.name, o.created_at,
                       o.updated_at, latest_review.notes, o.description,
                       o.location, o.contact
                FROM organizations o
                JOIN verification_statuses status ON status.id = o.status_id
                LEFT JOIN LATERAL (
                    SELECT od.document_number, od.expires_at
                    FROM organization_documents od
                    WHERE od.organization_id = o.id
                      AND od.document_type = 'license'
                    ORDER BY od.created_at DESC, od.id DESC
                    LIMIT 1
                ) document ON TRUE
                LEFT JOIN LATERAL (
                    SELECT vr.notes
                    FROM verification_reviews vr
                    WHERE vr.organization_id = o.id
                    ORDER BY vr.reviewed_at DESC, vr.id DESC
                    LIMIT 1
                ) latest_review ON TRUE
                WHERE o.submitted_by = %s
                ORDER BY o.created_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [self._to_entity(row) for row in rows if row is not None]

    def get_tracking_records(self) -> list[OrganizationTrackingRecord]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    o.id,
                    o.name,
                    o.organization_type,
                    o.location,
                    o.latitude,
                    o.longitude,
                    current_status.name,
                    o.created_at,
                    o.updated_at,
                    review_status.name,
                    COALESCE(reviewer.full_name, reviewer.email),
                    review.notes,
                    review.reviewed_at
                FROM organizations o
                JOIN verification_statuses current_status
                    ON current_status.id = o.status_id
                LEFT JOIN verification_reviews review
                    ON review.organization_id = o.id
                LEFT JOIN verification_statuses review_status
                    ON review_status.id = review.status_id
                LEFT JOIN users reviewer
                    ON reviewer.id = review.reviewer_id
                ORDER BY o.updated_at DESC, o.name ASC,
                    review.reviewed_at DESC NULLS LAST, review.id DESC
                """
            ).fetchall()

        records: dict[str, dict] = {}
        for row in rows:
            record = records.setdefault(row[0], {
                "organization_id": row[0],
                "organization_name": row[1],
                "organization_type": row[2],
                "location": row[3],
                "latitude": row[4],
                "longitude": row[5],
                "status": OrganizationStatus(row[6]),
                "submitted_at": row[7],
                "updated_at": row[8],
                "review_history": [],
            })
            if row[12] is not None and row[9] is not None:
                record["review_history"].append(OrganizationReviewEvent(
                    status=OrganizationStatus(row[9]),
                    reviewer_name=row[10],
                    notes=row[11],
                    reviewed_at=row[12],
                ))

        return [OrganizationTrackingRecord(**record) for record in records.values()]

    def get_public_map_entries(self) -> list[OrganizationMapEntry]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT o.id, o.name, o.organization_type, o.location, o.latitude, o.longitude
                FROM organizations o
                JOIN verification_statuses status ON status.id = o.status_id
                JOIN LATERAL (
                    SELECT od.expires_at
                    FROM organization_documents od
                    WHERE od.organization_id = o.id
                      AND od.document_type = 'license'
                    ORDER BY od.created_at DESC, od.id DESC
                    LIMIT 1
                ) license ON TRUE
                WHERE status.name = %s
                  AND license.expires_at >= CURRENT_DATE
                ORDER BY o.name ASC
                """,
                (OrganizationStatus.VERIFIED.value,),
            ).fetchall()

        return [OrganizationMapEntry(
            organization_id=row[0],
            organization_name=row[1],
            organization_type=row[2],
            location=row[3],
            latitude=row[4],
            longitude=row[5],
        ) for row in rows]

    def approve(
        self,
        organization_id: str,
        reviewer_id: str,
    ) -> Organization | None:
        with get_connection() as connection:
            with connection.transaction():
                updated = connection.execute(
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
                      AND status_id = (
                          SELECT id
                          FROM verification_statuses
                          WHERE name = %s
                      )
                      AND (
                          SELECT od.expires_at
                          FROM organization_documents od
                          WHERE od.organization_id = organizations.id
                            AND od.document_type = 'license'
                          ORDER BY od.created_at DESC, od.id DESC
                          LIMIT 1
                      ) >= CURRENT_DATE
                    RETURNING id
                    """,
                    (
                        OrganizationStatus.VERIFIED.value,
                        reviewer_id,
                        organization_id,
                        OrganizationStatus.PENDING.value,
                    ),
                ).fetchone()

                if updated is None:
                    return None

                applicant = connection.execute(
                    "SELECT submitted_by FROM organizations WHERE id = %s",
                    (organization_id,),
                ).fetchone()
                if applicant is None:
                    return None
                connection.execute(
                    """
                    INSERT INTO user_organizations (user_id, organization_id)
                    VALUES (%s, %s)
                    ON CONFLICT (user_id, organization_id) DO NOTHING
                    """,
                    (applicant[0], organization_id),
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

                # CAR-131: Keep the audit event inside this transaction.
                PostgresAuditLogRepository().record_on_connection(
                    connection,
                    actor_user_id=reviewer_id,
                    actor_role="carelife_admin",
                    action="organization.verification.approved",
                    target_type="organization",
                    target_id=organization_id,
                )

        return self.get_by_organization_id(organization_id)

    def reject(
        self,
        organization_id: str,
        reviewer_id: str,
        message: str | None = None,
    ) -> Organization | None:
        with get_connection() as connection:
            with connection.transaction():
                updated = connection.execute(
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
                      AND status_id = (
                          SELECT id
                          FROM verification_statuses
                          WHERE name = %s
                      )
                    RETURNING id
                    """,
                    (
                        OrganizationStatus.REJECTED.value,
                        reviewer_id,
                        organization_id,
                        OrganizationStatus.PENDING.value,
                    ),
                ).fetchone()

                if updated is None:
                    return None

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

                # CAR-131: Keep the audit event inside this transaction.
                PostgresAuditLogRepository().record_on_connection(
                    connection,
                    actor_user_id=reviewer_id,
                    actor_role="carelife_admin",
                    action="organization.verification.rejected",
                    target_type="organization",
                    target_id=organization_id,
                )

        return self.get_by_organization_id(organization_id)

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
                    o.latitude,
                    o.longitude,
                    o.contact
                FROM organizations o
                JOIN verification_statuses status
                    ON status.id = o.status_id
                JOIN LATERAL (
                    SELECT od.expires_at
                    FROM organization_documents od
                    WHERE od.organization_id = o.id
                      AND od.document_type = 'license'
                    ORDER BY od.created_at DESC
                    LIMIT 1
                ) license ON TRUE
                WHERE o.organization_type = 'daycare'
                  AND status.name = %s
                  AND license.expires_at >= CURRENT_DATE
                  AND (
                      %s::text IS NULL
                      OR o.name ILIKE %s
                      OR COALESCE(o.location, '') ILIKE %s
                      OR COALESCE(o.description, '') ILIKE %s
                  )
                  AND (
                      %s::text IS NULL
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

    def get_elder_care_directory(
        self,
        search: str | None = None,
        location: str | None = None,
        min_capacity: int | None = None,
        max_capacity: int | None = None,
        facility: str | None = None,
    ) -> list[ElderCareDirectoryEntry]:
        search_text = search.strip() if search else None
        location_text = location.strip() if location else None
        facility_text = facility.strip() if facility else None

        if not search_text:
            search_text = None
        if not location_text:
            location_text = None
        if not facility_text:
            facility_text = None

        search_pattern = (
            f"%{search_text}%"
            if search_text is not None
            else None
        )
        location_pattern = (
            f"%{location_text}%"
            if location_text is not None
            else None
        )
        facility_pattern = (
            f"%{facility_text}%"
            if facility_text is not None
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
                    o.latitude,
                    o.longitude,
                    o.contact,
                    o.capacity,
                    o.age_range,
                    o.opening_hours,
                    o.facilities,
                    o.fees
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
                ) license ON TRUE
                WHERE o.organization_type = 'elderly_care'
                  AND status.name = %s
                  AND license.expires_at >= CURRENT_DATE
                  AND (
                      %s::text IS NULL
                      OR o.name ILIKE %s
                      OR COALESCE(o.location, '') ILIKE %s
                      OR COALESCE(o.description, '') ILIKE %s
                      OR COALESCE(o.contact, '') ILIKE %s
                      OR COALESCE(o.age_range, '') ILIKE %s
                      OR COALESCE(o.opening_hours, '') ILIKE %s
                      OR COALESCE(o.facilities, '') ILIKE %s
                      OR COALESCE(o.fees, '') ILIKE %s
                  )
                  AND (
                      %s::text IS NULL
                      OR COALESCE(o.location, '') ILIKE %s
                  )
                  AND (
                      %s::integer IS NULL
                      OR o.capacity >= %s
                  )
                  AND (
                      %s::integer IS NULL
                      OR o.capacity <= %s
                  )
                  AND (
                      %s::text IS NULL
                      OR COALESCE(o.facilities, '') ILIKE %s
                  )
                ORDER BY o.name ASC
                """,
                (
                    OrganizationStatus.VERIFIED.value,
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    location_pattern,
                    location_pattern,
                    min_capacity,
                    min_capacity,
                    max_capacity,
                    max_capacity,
                    facility_pattern,
                    facility_pattern,
                ),
            ).fetchall()

        return [
            self._to_elder_care_directory_entry(row)
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
                    o.latitude,
                    o.longitude,
                    o.contact
                FROM organizations o
                JOIN verification_statuses status
                    ON status.id = o.status_id
                JOIN LATERAL (
                    SELECT od.expires_at
                    FROM organization_documents od
                    WHERE od.organization_id = o.id
                      AND od.document_type = 'license'
                    ORDER BY od.created_at DESC
                    LIMIT 1
                ) license ON TRUE
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
            latitude=row[5],
            longitude=row[6],
            contact=row[7],
        )

    @staticmethod
    def _to_elder_care_directory_entry(
        row,
    ) -> ElderCareDirectoryEntry | None:
        if row is None:
            return None

        return ElderCareDirectoryEntry(
            organization_id=row[0],
            organization_name=row[1],
            organization_type=row[2],
            description=row[3],
            location=row[4],
            latitude=row[5],
            longitude=row[6],
            contact=row[7],
            capacity=row[8],
            age_range=row[9],
            opening_hours=row[10],
            facilities=row[11],
            fees=row[12],
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
            description=row[10],
            location=row[11],
            contact=row[12],
        )

    def expire_verified_organizations(self) -> int:
        expired_count = 0

        with get_connection() as connection:
            with connection.transaction():
                expired_organizations = connection.execute(
                    """
                    SELECT
                        o.id,
                        o.name,
                        document.document_type,
                        document.expires_at
                    FROM organizations o
                    JOIN verification_statuses status
                        ON status.id = o.status_id
                    JOIN LATERAL (
                        SELECT current_documents.document_type,
                               current_documents.expires_at
                        FROM (
                            SELECT DISTINCT ON (
                                LOWER(od.document_type)
                            ) od.document_type, od.expires_at
                            FROM organization_documents od
                            WHERE od.organization_id = o.id
                              AND LOWER(od.document_type) IN (
                                  'license', 'registration',
                                  'registration_certificate'
                              )
                            ORDER BY LOWER(od.document_type),
                                     od.created_at DESC, od.id DESC
                        ) current_documents
                        ORDER BY current_documents.expires_at ASC
                        LIMIT 1
                    ) document ON TRUE
                    WHERE status.name = %s
                      AND document.expires_at < CURRENT_DATE
                    ORDER BY o.id
                    FOR UPDATE OF o
                    """,
                    (OrganizationStatus.VERIFIED.value,),
                ).fetchall()

                for (
                    organization_id,
                    organization_name,
                    document_type,
                    expires_at,
                ) in expired_organizations:
                    updated = connection.execute(
                        """
                        UPDATE organizations
                        SET
                            status_id = (
                                SELECT id
                                FROM verification_statuses
                                WHERE name = %s
                            ),
                            updated_at = CURRENT_TIMESTAMP,
                            updated_by = NULL
                        WHERE id = %s
                          AND status_id = (
                              SELECT id
                              FROM verification_statuses
                              WHERE name = %s
                          )
                        RETURNING id
                        """,
                        (
                            OrganizationStatus.EXPIRED.value,
                            organization_id,
                            OrganizationStatus.VERIFIED.value,
                        ),
                    ).fetchone()

                    if updated is None:
                        continue

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
                            CURRENT_TIMESTAMP
                        )
                        """,
                        (
                            organization_id,
                            OrganizationStatus.EXPIRED.value,
                            (
                                f"{document_type.replace('_', ' ').title()} "
                                f"for {organization_name} expired "
                                f"on {expires_at.isoformat()}; verification "
                                "automatically changed to expired."
                            ),
                        ),
                    )

                    expired_count += 1

        return expired_count

    def create_license_expiry_reminders(
        self,
        reminder_days: int,
    ) -> int:
        if reminder_days <= 0:
            raise ValueError(
                "Reminder period must be greater than zero"
            )

        reminders_created = 0

        with get_connection() as connection:
            with connection.transaction():
                expiring_organizations = connection.execute(
                    """
                    SELECT
                        o.id,
                        o.name,
                        document.document_type,
                        document.expires_at,
                        recipient.user_id
                    FROM organizations o
                    JOIN verification_statuses status
                        ON status.id = o.status_id
                    JOIN organization_documents document
                        ON document.organization_id = o.id
                       AND LOWER(document.document_type) IN (
                           'license', 'registration',
                           'registration_certificate'
                       )
                    CROSS JOIN LATERAL (
                        SELECT o.submitted_by AS user_id
                        UNION
                        SELECT uo.user_id
                        FROM user_organizations uo
                        WHERE uo.organization_id = o.id
                    ) recipient
                    JOIN users notification_user
                        ON notification_user.id = recipient.user_id
                       AND notification_user.is_active = TRUE
                    WHERE status.name = %s
                      AND document.expires_at >= CURRENT_DATE
                      AND document.expires_at
                          <= CURRENT_DATE + %s
                    ORDER BY
                        o.id,
                        document.document_type,
                        document.expires_at,
                        recipient.user_id
                    """,
                    (
                        OrganizationStatus.VERIFIED.value,
                        reminder_days,
                    ),
                ).fetchall()

                for (
                    organization_id,
                    organization_name,
                    document_type,
                    expires_at,
                    user_id,
                ) in expiring_organizations:
                    event_key = (
                        "organization-document-expiry:"
                        f"{organization_id}:"
                        f"{document_type}:"
                        f"{expires_at.isoformat()}:"
                        f"reminder:{user_id}"
                    )

                    message = (
                        f"The {document_type.replace('_', ' ')} for "
                        f"{organization_name} expires on "
                        f"{expires_at.isoformat()}. Please renew it before "
                        "expiry to keep the organization's verification "
                        "current."
                    )

                    inserted = connection.execute(
                        """
                        INSERT INTO notifications (
                            id,
                            user_id,
                            organization_id,
                            notification_type,
                            title,
                            message,
                            document_type,
                            document_expires_at,
                            event_key,
                            is_read,
                            created_at
                        )
                        VALUES (
                            gen_random_uuid()::text,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            FALSE,
                            CURRENT_TIMESTAMP
                        )
                        ON CONFLICT (event_key) DO NOTHING
                        RETURNING id
                        """,
                        (
                            user_id,
                            organization_id,
                            "organization_license_expiry",
                            "Organization document expiring soon",
                            message,
                            document_type,
                            expires_at,
                            event_key,
                        ),
                    ).fetchone()

                    if inserted is not None:
                        reminders_created += 1

        return reminders_created

    def get_pending_license_expiry_emails(self) -> list[dict[str, str]]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    n.id,
                    u.email,
                    o.name,
                    n.document_type,
                    n.document_expires_at,
                    n.message
                FROM notifications n
                JOIN users u ON u.id = n.user_id
                JOIN organizations o ON o.id = n.organization_id
                JOIN verification_statuses status ON status.id = o.status_id
                WHERE n.notification_type = 'organization_license_expiry'
                  AND n.email_sent_at IS NULL
                  AND n.document_type IS NOT NULL
                  AND n.document_expires_at IS NOT NULL
                  AND u.is_active = TRUE
                  AND status.name = %s
                  AND n.document_expires_at >= CURRENT_DATE
                ORDER BY n.created_at, n.id
                """,
                (OrganizationStatus.VERIFIED.value,),
            ).fetchall()

        return [
            {
                "notification_id": row[0],
                "email": row[1],
                "organization_name": row[2],
                "document_type": row[3],
                "expires_on": row[4].isoformat(),
                "message": row[5],
            }
            for row in rows
        ]

    def mark_license_expiry_email_sent(
        self,
        notification_id: str,
    ) -> bool:
        with get_connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    """
                    UPDATE notifications
                    SET email_sent_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                      AND notification_type = 'organization_license_expiry'
                      AND email_sent_at IS NULL
                    RETURNING id
                    """,
                    (notification_id,),
                ).fetchone()
        return row is not None
