from datetime import datetime

from app.application.interfaces.child import AttendanceRepository
from app.domain.entities.child import Attendance, DailyUpdate
from app.infrastructure.database.connection import get_connection


class PostgresAttendanceRepository(AttendanceRepository):

    def create_check_in(
        self,
        attendance: Attendance,
    ) -> Attendance:
        with get_connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    """
                    INSERT INTO daycare_attendance (
                        id,
                        enrollment_id,
                        attendance_date,
                        check_in_at,
                        recorded_by
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (
                        enrollment_id,
                        attendance_date
                    ) DO NOTHING
                    RETURNING id
                    """,
                    (
                        attendance.id,
                        attendance.enrollment_id,
                        attendance.attendance_date,
                        attendance.check_in_at,
                        attendance.recorded_by,
                    ),
                ).fetchone()

                if row is None:
                    raise ValueError(
                        "Attendance has already been recorded "
                        "for this enrollment today"
                    )

        saved = self.get_by_id(attendance.id)

        if saved is None:
            raise RuntimeError("Could not save attendance")

        return saved

    def get_by_id(
        self,
        attendance_id: str,
    ) -> Attendance | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    enrollment_id,
                    attendance_date,
                    check_in_at,
                    check_out_at,
                    recorded_by
                FROM daycare_attendance
                WHERE id = %s
                """,
                (attendance_id,),
            ).fetchone()

        return self._attendance_from_row(row)

    def check_out(
        self,
        attendance_id: str,
        when: datetime,
    ) -> Attendance | None:
        with get_connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    """
                    UPDATE daycare_attendance
                    SET check_out_at = %s
                    WHERE id = %s
                      AND check_out_at IS NULL
                      AND %s >= check_in_at
                    RETURNING
                        id,
                        enrollment_id,
                        attendance_date,
                        check_in_at,
                        check_out_at,
                        recorded_by
                    """,
                    (
                        when,
                        attendance_id,
                        when,
                    ),
                ).fetchone()

        return self._attendance_from_row(row)

    def list_for_child(
        self,
        child_id: str,
        daycare_organization_id: str | None = None,
    ) -> list[Attendance]:
        query = """
            SELECT
                a.id,
                a.enrollment_id,
                a.attendance_date,
                a.check_in_at,
                a.check_out_at,
                a.recorded_by
            FROM daycare_attendance a
            JOIN daycare_enrollments e
                ON e.id = a.enrollment_id
            WHERE e.child_id = %s
        """
        params: list[object] = [child_id]

        if daycare_organization_id is not None:
            query += """
                AND e.daycare_organization_id = %s
            """
            params.append(daycare_organization_id)

        query += """
            ORDER BY a.attendance_date DESC, a.check_in_at DESC
        """

        with get_connection() as connection:
            rows = connection.execute(query, params).fetchall()

        return [
            self._attendance_from_row(row)
            for row in rows
        ]

    def has_approved_enrollment(
        self,
        child_id: str,
        daycare_organization_id: str,
    ) -> bool:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM daycare_enrollments
                WHERE child_id = %s
                  AND daycare_organization_id = %s
                  AND status = 'approved'
                LIMIT 1
                """,
                (
                    child_id,
                    daycare_organization_id,
                ),
            ).fetchone()

        return row is not None

    def create_daily_update(
        self,
        update: DailyUpdate,
    ) -> DailyUpdate:
        with get_connection() as connection:
            with connection.transaction():
                connection.execute(
                    """
                    INSERT INTO daycare_daily_updates (
                        id,
                        child_id,
                        daycare_organization_id,
                        update_date,
                        notes,
                        recorded_by,
                        created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        update.id,
                        update.child_id,
                        update.daycare_organization_id,
                        update.update_date,
                        update.notes,
                        update.recorded_by,
                        update.created_at,
                    ),
                )

        return update

    def list_daily_updates(
        self,
        child_id: str,
        daycare_organization_id: str | None = None,
    ) -> list[DailyUpdate]:
        query = """
            SELECT
                id,
                child_id,
                daycare_organization_id,
                update_date,
                notes,
                recorded_by,
                created_at
            FROM daycare_daily_updates
            WHERE child_id = %s
        """
        params: list[object] = [child_id]

        if daycare_organization_id is not None:
            query += """
                AND daycare_organization_id = %s
            """
            params.append(daycare_organization_id)

        query += """
            ORDER BY update_date DESC, created_at DESC
        """

        with get_connection() as connection:
            rows = connection.execute(query, params).fetchall()

        return [
            self._daily_update_from_row(row)
            for row in rows
        ]

    @staticmethod
    def _attendance_from_row(row) -> Attendance | None:
        if row is None:
            return None

        return Attendance(
            id=row[0],
            enrollment_id=row[1],
            attendance_date=row[2],
            check_in_at=row[3],
            check_out_at=row[4],
            recorded_by=row[5],
        )

    @staticmethod
    def _daily_update_from_row(row) -> DailyUpdate:
        return DailyUpdate(
            id=row[0],
            child_id=row[1],
            daycare_organization_id=row[2],
            update_date=row[3],
            notes=row[4],
            recorded_by=row[5],
            created_at=row[6],
        )