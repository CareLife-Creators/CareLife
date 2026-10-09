from app.domain.entities.organization import (
    OrganizationStatus,
)
from app.application.interfaces.enrollment import (
    EnrollmentRepository,
)
from app.domain.entities.enrollment import (
    Enrollment,
    EnrollmentStatus,
)
from app.infrastructure.database.connection import (
    get_connection,
)


class PostgresEnrollmentRepository(
    EnrollmentRepository
):

    def create(
        self,
        enrollment: Enrollment,
    ) -> Enrollment:

        with get_connection() as connection:
            with connection.transaction():

                organization_row = connection.execute(
                    """
                    SELECT
                        capacity
                    FROM organizations
                    WHERE id = %s
                      AND organization_type = 'daycare'
                    FOR UPDATE
                    """,
                    (
                        enrollment.daycare_organization_id,
                    ),
                ).fetchone()

                if organization_row is None:
                    raise ValueError(
                        "Daycare organization not found"
                    )

                capacity = organization_row[0]

                approved_row = connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM daycare_enrollments
                    WHERE daycare_organization_id = %s
                      AND status = %s
                    """,
                    (
                        enrollment.daycare_organization_id,
                        EnrollmentStatus.APPROVED.value,
                    ),
                ).fetchone()

                approved_count = approved_row[0]

                if approved_count >= capacity:
                    raise ValueError(
                        "Daycare has no available capacity"
                    )

                child_row = connection.execute(
                    """
                    SELECT
                        parent_id,
                        daycare_organization_id
                    FROM children
                    WHERE id = %s
                    FOR UPDATE
                    """,
                    (
                        enrollment.child_id,
                    ),
                ).fetchone()

                if child_row is None:
                    raise ValueError(
                        "Child record not found"
                    )

                current_daycare_id = child_row[1]

                if (
                    current_daycare_id is not None
                    and current_daycare_id
                    != enrollment.daycare_organization_id
                ):
                    raise ValueError(
                        "Child is already enrolled at another daycare"
                    )

                active_enrollment = connection.execute(
                    """
                    SELECT 1
                    FROM daycare_enrollments
                    WHERE child_id = %s
                      AND daycare_organization_id = %s
                      AND status IN (
                          'pending',
                          'waitlisted',
                          'approved'
                      )
                    LIMIT 1
                    """,
                    (
                        enrollment.child_id,
                        enrollment.daycare_organization_id,
                    ),
                ).fetchone()

                if active_enrollment is not None:
                    raise ValueError(
                        "An active enrollment already exists for this child"
                    )

                connection.execute(
                    """
                    INSERT INTO daycare_enrollments (
                        id,
                        child_id,
                        daycare_organization_id,
                        status,
                        requested_at,
                        reviewed_at,
                        reviewed_by,
                        cancelled_at,
                        decision_message
                    )
                    VALUES (
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
                        enrollment.id,
                        enrollment.child_id,
                        enrollment.daycare_organization_id,
                        enrollment.status.value,
                        enrollment.requested_at,
                        enrollment.reviewed_at,
                        enrollment.reviewed_by,
                        enrollment.cancelled_at,
                        enrollment.decision_message,
                    ),
                )

        return self.get_by_id(enrollment.id)  # type: ignore[return-value]

    def get_by_id(
        self,
        enrollment_id: str,
    ) -> Enrollment | None:

        with get_connection() as connection:

            row = connection.execute(
                """
                SELECT
                    id,
                    child_id,
                    daycare_organization_id,
                    status,
                    requested_at,
                    reviewed_at,
                    reviewed_by,
                    cancelled_at,
                    decision_message
                FROM daycare_enrollments
                WHERE id = %s
                """,
                (
                    enrollment_id,
                ),
            ).fetchone()

        return self._from_row(row)

    def list_by_parent(
        self,
        parent_id: str,
    ) -> list[Enrollment]:

        with get_connection() as connection:

            rows = connection.execute(
                """
                SELECT
                    e.id,
                    e.child_id,
                    e.daycare_organization_id,
                    e.status,
                    e.requested_at,
                    e.reviewed_at,
                    e.reviewed_by,
                    e.cancelled_at,
                    e.decision_message
                FROM daycare_enrollments e
                JOIN children c
                    ON c.id = e.child_id
                WHERE c.parent_id = %s
                ORDER BY e.requested_at DESC
                """,
                (
                    parent_id,
                ),
            ).fetchall()

        return [
            self._from_row(row)
            for row in rows
            if row is not None
        ]

    def list_pending_by_daycare(
        self,
        organization_id: str,
    ) -> list[Enrollment]:

        with get_connection() as connection:

            rows = connection.execute(
                """
                SELECT
                    id,
                    child_id,
                    daycare_organization_id,
                    status,
                    requested_at,
                    reviewed_at,
                    reviewed_by,
                    cancelled_at,
                    decision_message
                FROM daycare_enrollments
                WHERE daycare_organization_id = %s
                  AND status IN (
                      'pending',
                      'waitlisted'
                  )
                ORDER BY requested_at ASC
                """,
                (
                    organization_id,
                ),
            ).fetchall()

        return [
            self._from_row(row)
            for row in rows
            if row is not None
        ]

    def review(
        self,
        enrollment_id: str,
        status: EnrollmentStatus,
        reviewer_id: str,
        message: str | None = None,
    ) -> Enrollment | None:

        with get_connection() as connection:
            with connection.transaction():

                row = connection.execute(
                    """
                    SELECT
                        id,
                        child_id,
                        daycare_organization_id,
                        status
                    FROM daycare_enrollments
                    WHERE id = %s
                    FOR UPDATE
                    """,
                    (
                        enrollment_id,
                    ),
                ).fetchone()

                if row is None:
                    return None

                current_status = EnrollmentStatus(
                    row[3]
                )

                if current_status not in (
                    EnrollmentStatus.PENDING,
                    EnrollmentStatus.WAITLISTED,
                ):
                    raise ValueError(
                        "Only pending or waitlisted enrollments can be reviewed"
                    )

                child_id = row[1]
                daycare_id = row[2]

                if status == EnrollmentStatus.APPROVED:

                    # CAR-46 FIX:
                    # Check daycare verification and license validity.
                    organization_row = connection.execute(
                        """
                        SELECT
                            o.capacity
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
                        FOR UPDATE OF o
                        """,
                        (
                            daycare_id,
                            OrganizationStatus.VERIFIED.value,
                        ),
                    ).fetchone()

                    if organization_row is None:
                        raise ValueError(
                            "Daycare is not currently eligible for enrollment approval"
                        )

                    capacity = organization_row[0]

                    approved_row = connection.execute(
                        """
                        SELECT COUNT(*)
                        FROM daycare_enrollments
                        WHERE daycare_organization_id = %s
                          AND status = %s
                        """,
                        (
                            daycare_id,
                            EnrollmentStatus.APPROVED.value,
                        ),
                    ).fetchone()

                    approved_count = approved_row[0]

                    if approved_count >= capacity:
                        raise ValueError(
                            "Daycare has no available capacity"
                        )

                    child_row = connection.execute(
                        """
                        SELECT
                            daycare_organization_id
                        FROM children
                        WHERE id = %s
                        FOR UPDATE
                        """,
                        (
                            child_id,
                        ),
                    ).fetchone()

                    if child_row is None:
                        raise ValueError(
                            "Child record not found"
                        )

                    current_daycare_id = child_row[0]

                    if (
                        current_daycare_id is not None
                        and current_daycare_id != daycare_id
                    ):
                        raise ValueError(
                            "Child is already enrolled at another daycare"
                        )

                    connection.execute(
                        """
                        UPDATE children
                        SET
                            daycare_organization_id = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        """,
                        (
                            daycare_id,
                            child_id,
                        ),
                    )

                connection.execute(
                    """
                    UPDATE daycare_enrollments
                    SET
                        status = %s,
                        reviewed_at = CURRENT_TIMESTAMP,
                        reviewed_by = %s,
                        decision_message = %s
                    WHERE id = %s
                    """,
                    (
                        status.value,
                        reviewer_id,
                        message,
                        enrollment_id,
                    ),
                )

        return self.get_by_id(enrollment_id)

    def cancel(
        self,
        enrollment_id: str,
    ) -> Enrollment | None:

        with get_connection() as connection:
            with connection.transaction():

                row = connection.execute(
                    """
                    SELECT
                        child_id,
                        daycare_organization_id,
                        status
                    FROM daycare_enrollments
                    WHERE id = %s
                    FOR UPDATE
                    """,
                    (
                        enrollment_id,
                    ),
                ).fetchone()

                if row is None:
                    return None

                current_status = EnrollmentStatus(
                    row[2]
                )

                if current_status not in (
                    EnrollmentStatus.PENDING,
                    EnrollmentStatus.WAITLISTED,
                    EnrollmentStatus.APPROVED,
                ):
                    raise ValueError(
                        "Enrollment cannot be cancelled in its current state"
                    )

                if current_status == EnrollmentStatus.APPROVED:

                    connection.execute(
                        """
                        UPDATE children
                        SET
                            daycare_organization_id = NULL,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                          AND daycare_organization_id = %s
                        """,
                        (
                            row[0],
                            row[1],
                        ),
                    )

                connection.execute(
                    """
                    UPDATE daycare_enrollments
                    SET
                        status = %s,
                        cancelled_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (
                        EnrollmentStatus.CANCELLED.value,
                        enrollment_id,
                    ),
                )

        return self.get_by_id(enrollment_id)

    @staticmethod
    def _from_row(
        row,
    ) -> Enrollment | None:

        if row is None:
            return None

        return Enrollment(
            id=row[0],
            child_id=row[1],
            daycare_organization_id=row[2],
            status=EnrollmentStatus(row[3]),
            requested_at=row[4],
            reviewed_at=row[5],
            reviewed_by=row[6],
            cancelled_at=row[7],
            decision_message=row[8],
        )