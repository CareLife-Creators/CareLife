from app.application.use_cases.attendance import AttendanceService
from app.application.use_cases.children import ChildService

from app.infrastructure.repositories.attendance import (
    PostgresAttendanceRepository,
)
from app.infrastructure.repositories.child import (
    PostgresChildRepository,
)
from app.infrastructure.repositories.enrollment import (
    PostgresEnrollmentRepository,
)


def get_child_service() -> ChildService:
    return ChildService(
        PostgresChildRepository()
    )


def get_attendance_service() -> AttendanceService:
    return AttendanceService(
        attendance_repository=PostgresAttendanceRepository(),
        enrollment_repository=PostgresEnrollmentRepository(),
        child_repository=PostgresChildRepository(),
    )