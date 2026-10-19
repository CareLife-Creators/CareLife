from datetime import datetime, timezone
from uuid import uuid4

from app.application.interfaces.caregiver_booking import (
    CaregiverBookingRepository,
)
from app.domain.entities.caregiver_booking import (
    CaregiverAppointment,
    CaregiverAppointmentStatus,
    CaregiverAvailability,
)
from app.infrastructure.database.connection import get_connection


class PostgresCaregiverBookingRepository(
    CaregiverBookingRepository
):
    @staticmethod
    def _availability_from_row(row) -> CaregiverAvailability:
        return CaregiverAvailability(
            id=row[0],
            caregiver_user_id=row[1],
            starts_at=row[2],
            ends_at=row[3],
            created_at=row[4],
        )

    @staticmethod
    def _appointment_from_row(row) -> CaregiverAppointment:
        return CaregiverAppointment(
            id=row[0],
            availability_id=row[1],
            caregiver_user_id=row[2],
            requester_user_id=row[3],
            service_type=row[4],
            starts_at=row[5],
            ends_at=row[6],
            status=CaregiverAppointmentStatus(row[7]),
            message=row[8],
            decision_message=row[9],
            reviewed_by=row[10],
            reviewed_at=row[11],
            created_at=row[12],
            updated_at=row[13],
        )

    @staticmethod
    def _appointment_select() -> str:
        return """
            SELECT
                id,
                availability_id,
                caregiver_user_id,
                requester_user_id,
                service_type,
                starts_at,
                ends_at,
                status,
                message,
                decision_message,
                reviewed_by,
                reviewed_at,
                created_at,
                updated_at
            FROM caregiver_appointments
        """

    def create_availability(
        self,
        caregiver_user_id: str,
        starts_at: datetime,
        ends_at: datetime,
    ) -> CaregiverAvailability:
        with get_connection() as connection:
            with connection.transaction():
                profile = connection.execute(
                    """
                    SELECT user_id
                    FROM caregiver_profiles
                    WHERE user_id = %s
                    FOR UPDATE
                    """,
                    (caregiver_user_id,),
                ).fetchone()

                if profile is None:
                    raise ValueError(
                        "Create a caregiver profile first."
                    )

                overlap = connection.execute(
                    """
                    SELECT 1
                    FROM caregiver_availability
                    WHERE caregiver_user_id = %s
                      AND starts_at < %s
                      AND ends_at > %s
                    LIMIT 1
                    """,
                    (
                        caregiver_user_id,
                        ends_at,
                        starts_at,
                    ),
                ).fetchone()

                if overlap is not None:
                    raise ValueError(
                        "This time overlaps an existing availability slot."
                    )

                row = connection.execute(
                    """
                    INSERT INTO caregiver_availability (
                        id,
                        caregiver_user_id,
                        starts_at,
                        ends_at,
                        created_at
                    )
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                    RETURNING
                        id,
                        caregiver_user_id,
                        starts_at,
                        ends_at,
                        created_at
                    """,
                    (
                        str(uuid4()),
                        caregiver_user_id,
                        starts_at,
                        ends_at,
                    ),
                ).fetchone()

        return self._availability_from_row(row)

    def list_availability_for_caregiver(
        self,
        caregiver_user_id: str,
    ) -> list[CaregiverAvailability]:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    caregiver_user_id,
                    starts_at,
                    ends_at,
                    created_at
                FROM caregiver_availability
                WHERE caregiver_user_id = %s
                  AND ends_at > CURRENT_TIMESTAMP
                ORDER BY starts_at ASC, id ASC
                """,
                (caregiver_user_id,),
            ).fetchall()

        return [
            self._availability_from_row(row)
            for row in rows
        ]

    def list_public_availability(
        self,
        caregiver_user_id: str,
    ) -> list[CaregiverAvailability]:
        with get_connection() as connection:
            profile = connection.execute(
                """
                SELECT 1
                FROM caregiver_profiles
                WHERE user_id = %s
                  AND verification_status = 'approved'
                """,
                (caregiver_user_id,),
            ).fetchone()

            if profile is None:
                raise LookupError(
                    "Approved caregiver not found."
                )

            rows = connection.execute(
                """
                SELECT
                    a.id,
                    a.caregiver_user_id,
                    a.starts_at,
                    a.ends_at,
                    a.created_at
                FROM caregiver_availability a
                WHERE a.caregiver_user_id = %s
                  AND a.starts_at > CURRENT_TIMESTAMP
                  AND NOT EXISTS (
                      SELECT 1
                      FROM caregiver_appointments ap
                      WHERE ap.availability_id = a.id
                        AND ap.status IN ('requested', 'accepted')
                  )
                ORDER BY a.starts_at ASC, a.id ASC
                """,
                (caregiver_user_id,),
            ).fetchall()

        return [
            self._availability_from_row(row)
            for row in rows
        ]

    def create_appointment(
        self,
        requester_user_id: str,
        availability_id: str,
        message: str | None,
    ) -> CaregiverAppointment:
        with get_connection() as connection:
            with connection.transaction():
                slot = connection.execute(
                    """
                    SELECT
                        a.id,
                        a.caregiver_user_id,
                        a.starts_at,
                        a.ends_at,
                        c.service_type
                    FROM caregiver_availability a
                    JOIN caregiver_profiles c
                      ON c.user_id = a.caregiver_user_id
                    WHERE a.id = %s
                      AND c.verification_status = 'approved'
                    FOR UPDATE OF a, c
                    """,
                    (availability_id,),
                ).fetchone()

                if slot is None:
                    raise ValueError(
                        "Approved caregiver or availability slot not found."
                    )

                slot_id, caregiver_id, starts_at, ends_at, service_type = (
                    slot
                )

                if starts_at <= datetime.now(timezone.utc):
                    raise ValueError(
                        "This availability slot has already started or expired."
                    )

                if caregiver_id == requester_user_id:
                    raise ValueError(
                        "A caregiver cannot book their own slot."
                    )

                existing = connection.execute(
                    """
                    SELECT 1
                    FROM caregiver_appointments
                    WHERE availability_id = %s
                      AND status IN ('requested', 'accepted')
                    LIMIT 1
                    """,
                    (slot_id,),
                ).fetchone()

                if existing is not None:
                    raise ValueError(
                        "This time slot is no longer available."
                    )

                row = connection.execute(
                    """
                    INSERT INTO caregiver_appointments (
                        id,
                        availability_id,
                        caregiver_user_id,
                        requester_user_id,
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
                        'requested', %s,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                    )
                    RETURNING
                        id,
                        availability_id,
                        caregiver_user_id,
                        requester_user_id,
                        service_type,
                        starts_at,
                        ends_at,
                        status,
                        message,
                        decision_message,
                        reviewed_by,
                        reviewed_at,
                        created_at,
                        updated_at
                    """,
                    (
                        str(uuid4()),
                        slot_id,
                        caregiver_id,
                        requester_user_id,
                        service_type,
                        starts_at,
                        ends_at,
                        message,
                    ),
                ).fetchone()

        return self._appointment_from_row(row)

    def get_appointment(
        self,
        appointment_id: str,
    ) -> CaregiverAppointment | None:
        with get_connection() as connection:
            row = connection.execute(
                self._appointment_select()
                + " WHERE id = %s",
                (appointment_id,),
            ).fetchone()

        if row is None:
            return None

        return self._appointment_from_row(row)

    def list_for_requester(
        self,
        requester_user_id: str,
    ) -> list[CaregiverAppointment]:
        with get_connection() as connection:
            rows = connection.execute(
                self._appointment_select()
                + """
                    WHERE requester_user_id = %s
                    ORDER BY created_at DESC, id DESC
                """,
                (requester_user_id,),
            ).fetchall()

        return [
            self._appointment_from_row(row)
            for row in rows
        ]

    def list_for_caregiver(
        self,
        caregiver_user_id: str,
    ) -> list[CaregiverAppointment]:
        with get_connection() as connection:
            rows = connection.execute(
                self._appointment_select()
                + """
                    WHERE caregiver_user_id = %s
                    ORDER BY starts_at ASC, id ASC
                """,
                (caregiver_user_id,),
            ).fetchall()

        return [
            self._appointment_from_row(row)
            for row in rows
        ]

    def decide_appointment(
        self,
        appointment_id: str,
        caregiver_user_id: str,
        status: CaregiverAppointmentStatus,
        message: str | None,
    ) -> CaregiverAppointment | None:
        with get_connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    """
                    UPDATE caregiver_appointments
                    SET
                        status = %s,
                        decision_message = %s,
                        reviewed_by = %s,
                        reviewed_at = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                      AND caregiver_user_id = %s
                      AND status = 'requested'
                    RETURNING
                        id,
                        availability_id,
                        caregiver_user_id,
                        requester_user_id,
                        service_type,
                        starts_at,
                        ends_at,
                        status,
                        message,
                        decision_message,
                        reviewed_by,
                        reviewed_at,
                        created_at,
                        updated_at
                    """,
                    (
                        status.value,
                        message,
                        caregiver_user_id,
                        appointment_id,
                        caregiver_user_id,
                    ),
                ).fetchone()

        if row is None:
            return None

        return self._appointment_from_row(row)