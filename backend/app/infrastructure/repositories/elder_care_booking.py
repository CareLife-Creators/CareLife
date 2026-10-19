from enum import Enum
from uuid import uuid4

from app.application.interfaces.elder_care_booking import (
    ElderCareBookingRepository,
)
from app.domain.entities.elder_care_booking import (
    ElderCareBooking,
    ElderCareBookingStatus,
    ElderCareBookingStatusHistory,
    ElderCareProviderType,
)
from app.domain.entities.user_context import Role
from app.infrastructure.database.connection import get_connection


BOOKING_SELECT = """
    SELECT
        b.id,
        b.resident_id,
        rp.organization_id,
        b.requester_user_id,
        b.provider_type,
        b.caregiver_user_id,
        b.organization_id,
        b.availability_id,
        b.service_type,
        b.starts_at,
        b.ends_at,
        b.status,
        b.message,
        b.decision_message,
        b.reviewed_by,
        b.reviewed_at,
        b.cancelled_by,
        b.completed_at,
        b.created_at,
        b.updated_at
    FROM elder_care_bookings AS b
    JOIN resident_profiles AS rp
      ON rp.id = b.resident_id
"""

HISTORY_SELECT = """
    SELECT
        id,
        booking_id,
        sequence_no,
        from_status,
        to_status,
        changed_by,
        note,
        created_at
    FROM elder_care_booking_status_history
"""


def _value(value):
    if isinstance(value, Enum):
        return value.value

    return value


class PostgresElderCareBookingRepository(
    ElderCareBookingRepository
):

    @staticmethod
    def _booking_from_row(row) -> ElderCareBooking:
        return ElderCareBooking(
            id=row[0],
            resident_id=row[1],
            resident_organization_id=row[2],
            requester_user_id=row[3],
            provider_type=ElderCareProviderType(row[4]),
            caregiver_user_id=row[5],
            organization_id=row[6],
            availability_id=row[7],
            service_type=row[8],
            starts_at=row[9],
            ends_at=row[10],
            status=ElderCareBookingStatus(row[11]),
            message=row[12],
            decision_message=row[13],
            reviewed_by=row[14],
            reviewed_at=row[15],
            cancelled_by=row[16],
            completed_at=row[17],
            created_at=row[18],
            updated_at=row[19],
        )

    @staticmethod
    def _history_from_row(
        row,
    ) -> ElderCareBookingStatusHistory:
        return ElderCareBookingStatusHistory(
            id=row[0],
            booking_id=row[1],
            sequence_no=row[2],
            from_status=(
                ElderCareBookingStatus(row[3])
                if row[3] is not None
                else None
            ),
            to_status=ElderCareBookingStatus(row[4]),
            changed_by=row[5],
            note=row[6],
            created_at=row[7],
        )

    @staticmethod
    def _append_history(
        connection,
        booking_id: str,
        previous_status: ElderCareBookingStatus | None,
        new_status: ElderCareBookingStatus,
        actor_user_id: str,
        note: str | None,
    ) -> None:
        sequence_row = connection.execute(
            """
            SELECT COALESCE(MAX(sequence_no), 0) + 1
            FROM elder_care_booking_status_history
            WHERE booking_id = %s
            """,
            (booking_id,),
        ).fetchone()

        sequence_no = sequence_row[0]

        connection.execute(
            """
            INSERT INTO elder_care_booking_status_history (
                id,
                booking_id,
                sequence_no,
                from_status,
                to_status,
                changed_by,
                note,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s,
                    CURRENT_TIMESTAMP)
            """,
            (
                str(uuid4()),
                booking_id,
                sequence_no,
                (
                    previous_status.value
                    if previous_status is not None
                    else None
                ),
                new_status.value,
                actor_user_id,
                note,
            ),
        )

    @staticmethod
    def _is_care_home_staff(
        connection,
        user_id: str,
        organization_id: str,
    ) -> bool:
        row = connection.execute(
            """
            SELECT 1
            FROM user_organizations AS uo
            JOIN users AS u
              ON u.id = uo.user_id
            JOIN roles AS r
              ON r.id = u.role_id
            WHERE uo.user_id = %s
              AND uo.organization_id = %s
              AND u.is_active = TRUE
              AND r.name = 'care_home_staff'
            LIMIT 1
            """,
            (user_id, organization_id),
        ).fetchone()

        return row is not None

    def is_care_home_staff(
        self,
        user_id: str,
        organization_id: str,
    ) -> bool:
        with get_connection() as connection:
            return self._is_care_home_staff(
                connection,
                user_id,
                organization_id,
            )

    def is_approved_elder_care_caregiver(
        self,
        user_id: str,
    ) -> bool:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM caregiver_profiles
                WHERE user_id = %s
                  AND service_type = 'elder_care_giver'
                  AND verification_status = 'approved'
                LIMIT 1
                """,
                (user_id,),
            ).fetchone()

        return row is not None

    def create_booking(
        self,
        requester_user_id: str,
        values: dict[str, object],
    ) -> ElderCareBooking:
        provider_type = _value(values["provider_type"])
        provider_id = str(values["provider_id"])
        resident_id = str(values["resident_id"])
        starts_at = values["starts_at"]
        ends_at = values["ends_at"]
        service_type = str(values["service_type"])
        message = values.get("message")

        with get_connection() as connection:
            with connection.transaction():
                resident = connection.execute(
                    """
                    SELECT organization_id, status
                    FROM resident_profiles
                    WHERE id = %s
                    FOR UPDATE
                    """,
                    (resident_id,),
                ).fetchone()

                if resident is None:
                    raise LookupError("Resident profile not found")

                resident_organization_id, resident_status = resident

                if resident_status != "active":
                    raise ValueError(
                        "Bookings require an active resident"
                    )

                consent = connection.execute(
                    """
                    SELECT 1
                    FROM resident_family_consents
                    WHERE resident_id = %s
                      AND organization_id = %s
                      AND family_representative_id = %s
                      AND status = 'active'
                    LIMIT 1
                    """,
                    (
                        resident_id,
                        resident_organization_id,
                        requester_user_id,
                    ),
                ).fetchone()

                if consent is None:
                    raise PermissionError(
                        "Active family consent is required "
                        "for this resident"
                    )

                caregiver_user_id = None
                organization_id = None
                availability_id = None

                if provider_type == ElderCareProviderType.CAREGIVER.value:
                    caregiver = connection.execute(
                        """
                        SELECT user_id
                        FROM caregiver_profiles
                        WHERE user_id = %s
                          AND service_type = 'elder_care_giver'
                          AND verification_status = 'approved'
                        FOR UPDATE
                        """,
                        (provider_id,),
                    ).fetchone()

                    if caregiver is None:
                        raise LookupError(
                            "Approved elder-care caregiver not found"
                        )

                    availability = connection.execute(
                        """
                        SELECT a.id
                        FROM caregiver_availability AS a
                        WHERE a.caregiver_user_id = %s
                          AND a.starts_at <= %s
                          AND a.ends_at >= %s
                          AND a.starts_at > CURRENT_TIMESTAMP
                        ORDER BY a.starts_at ASC
                        LIMIT 1
                        FOR UPDATE
                        """,
                        (
                            provider_id,
                            starts_at,
                            ends_at,
                        ),
                    ).fetchone()

                    if availability is None:
                        raise ValueError(
                            "The caregiver has no future availability "
                            "that covers the requested time"
                        )

                    availability_id = availability[0]
                    caregiver_user_id = provider_id

                    conflicting_appointment = connection.execute(
                        """
                        SELECT 1
                        FROM caregiver_appointments
                        WHERE caregiver_user_id = %s
                          AND status IN ('requested', 'accepted')
                          AND starts_at < %s
                          AND ends_at > %s

                        UNION ALL

                        SELECT 1
                        FROM elder_care_bookings
                        WHERE caregiver_user_id = %s
                          AND status IN ('requested', 'approved')
                          AND starts_at < %s
                          AND ends_at > %s

                        LIMIT 1
                        """,
                        (
                            provider_id,
                            ends_at,
                            starts_at,
                            provider_id,
                            ends_at,
                            starts_at,
                        ),
                    ).fetchone()

                    if conflicting_appointment is not None:
                        raise ValueError(
                            "The caregiver already has a booking "
                            "during this time"
                        )

                elif provider_type == ElderCareProviderType.CARE_HOME.value:
                    organization = connection.execute(
                        """
                        SELECT o.id
                        FROM organizations AS o
                        JOIN verification_statuses AS vs
                          ON vs.id = o.status_id
                        WHERE o.id = %s
                          AND o.organization_type = 'elderly_care'
                          AND vs.name = 'verified'
                        FOR UPDATE OF o
                        """,
                        (provider_id,),
                    ).fetchone()

                    if organization is None:
                        raise LookupError(
                            "Verified elder-care organization not found"
                        )

                    if provider_id != resident_organization_id:
                        raise PermissionError(
                            "A care-home service must belong to "
                            "the resident's registered care home"
                        )

                    organization_id = provider_id

                else:
                    raise ValueError("Unsupported provider type")

                resident_conflict = connection.execute(
                    """
                    SELECT 1
                    FROM elder_care_bookings
                    WHERE resident_id = %s
                      AND status IN ('requested', 'approved')
                      AND starts_at < %s
                      AND ends_at > %s
                    LIMIT 1
                    """,
                    (
                        resident_id,
                        ends_at,
                        starts_at,
                    ),
                ).fetchone()

                if resident_conflict is not None:
                    raise ValueError(
                        "The resident already has a booking "
                        "during this time"
                    )

                booking_id = str(uuid4())

                connection.execute(
                    """
                    INSERT INTO elder_care_bookings (
                        id,
                        resident_id,
                        requester_user_id,
                        provider_type,
                        caregiver_user_id,
                        organization_id,
                        availability_id,
                        service_type,
                        starts_at,
                        ends_at,
                        status,
                        message,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, 'requested', %s,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                    """,
                    (
                        booking_id,
                        resident_id,
                        requester_user_id,
                        provider_type,
                        caregiver_user_id,
                        organization_id,
                        availability_id,
                        service_type,
                        starts_at,
                        ends_at,
                        message,
                    ),
                )

                self._append_history(
                    connection=connection,
                    booking_id=booking_id,
                    previous_status=None,
                    new_status=ElderCareBookingStatus.REQUESTED,
                    actor_user_id=requester_user_id,
                    note="Booking requested",
                )

                row = connection.execute(
                    BOOKING_SELECT + " WHERE b.id = %s",
                    (booking_id,),
                ).fetchone()

        return self._booking_from_row(row)

    def get_booking(
        self,
        booking_id: str,
    ) -> ElderCareBooking | None:
        with get_connection() as connection:
            row = connection.execute(
                BOOKING_SELECT + " WHERE b.id = %s",
                (booking_id,),
            ).fetchone()

        if row is None:
            return None

        return self._booking_from_row(row)

    def list_for_user(
        self,
        user_id: str,
        role: Role,
    ) -> list[ElderCareBooking]:
        query = BOOKING_SELECT
        params: tuple[object, ...] = ()

        if role in {
            Role.FAMILY_REPRESENTATIVE,
            Role.PARENT_GUARDIAN,
        }:
            query += " WHERE b.requester_user_id = %s"
            params = (user_id,)

        elif role == Role.INDEPENDENT_CAREGIVER:
            query += " WHERE b.caregiver_user_id = %s"
            params = (user_id,)

        elif role == Role.CARE_HOME_STAFF:
            query += """
                WHERE rp.organization_id IN (
                    SELECT uo.organization_id
                    FROM user_organizations AS uo
                    JOIN users AS u
                      ON u.id = uo.user_id
                    JOIN roles AS r
                      ON r.id = u.role_id
                    WHERE uo.user_id = %s
                      AND u.is_active = TRUE
                      AND r.name = 'care_home_staff'
                )
            """
            params = (user_id,)

        elif role != Role.CARELIFE_ADMIN:
            raise PermissionError(
                "You cannot list elder-care bookings"
            )

        query += " ORDER BY b.created_at DESC, b.id DESC"

        with get_connection() as connection:
            rows = connection.execute(
                query,
                params,
            ).fetchall()

        return [
            self._booking_from_row(row)
            for row in rows
        ]

    def get_status_history(
        self,
        booking_id: str,
    ) -> list[ElderCareBookingStatusHistory]:
        with get_connection() as connection:
            rows = connection.execute(
                HISTORY_SELECT
                + """
                WHERE booking_id = %s
                ORDER BY sequence_no ASC
                """,
                (booking_id,),
            ).fetchall()

        return [
            self._history_from_row(row)
            for row in rows
        ]

    def transition_booking(
        self,
        booking_id: str,
        actor_user_id: str,
        new_status: ElderCareBookingStatus,
        allowed_current_statuses: tuple[
            ElderCareBookingStatus, ...
        ],
        note: str | None,
    ) -> ElderCareBooking:
        note = note.strip() if note else None

        with get_connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    BOOKING_SELECT
                    + " WHERE b.id = %s FOR UPDATE OF b",
                    (booking_id,),
                ).fetchone()

                if row is None:
                    raise LookupError(
                        "Elder-care booking not found"
                    )

                current_booking = self._booking_from_row(row)

                if (
                    current_booking.status
                    not in allowed_current_statuses
                ):
                    raise ValueError(
                        "This booking cannot transition "
                        "from its current status"
                    )

                if new_status in {
                    ElderCareBookingStatus.APPROVED,
                    ElderCareBookingStatus.REJECTED,
                }:
                    connection.execute(
                        """
                        UPDATE elder_care_bookings
                        SET status = %s,
                            decision_message = %s,
                            reviewed_by = %s,
                            reviewed_at = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        """,
                        (
                            new_status.value,
                            note,
                            actor_user_id,
                            booking_id,
                        ),
                    )

                elif new_status == ElderCareBookingStatus.CANCELLED:
                    connection.execute(
                        """
                        UPDATE elder_care_bookings
                        SET status = %s,
                            cancelled_by = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        """,
                        (
                            new_status.value,
                            actor_user_id,
                            booking_id,
                        ),
                    )

                elif new_status == ElderCareBookingStatus.COMPLETED:
                    connection.execute(
                        """
                        UPDATE elder_care_bookings
                        SET status = %s,
                            completed_at = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        """,
                        (
                            new_status.value,
                            booking_id,
                        ),
                    )

                else:
                    raise ValueError(
                        "Unsupported booking status transition"
                    )

                self._append_history(
                    connection=connection,
                    booking_id=booking_id,
                    previous_status=current_booking.status,
                    new_status=new_status,
                    actor_user_id=actor_user_id,
                    note=note,
                )

                updated_row = connection.execute(
                    BOOKING_SELECT + " WHERE b.id = %s",
                    (booking_id,),
                ).fetchone()

        return self._booking_from_row(updated_row)