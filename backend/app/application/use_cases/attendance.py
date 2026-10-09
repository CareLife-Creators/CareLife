from datetime import datetime, timezone
from uuid import uuid4
from zoneinfo import ZoneInfo

from app.application.interfaces.child import (
    AttendanceRepository,
    ChildRepository,
)
from app.application.interfaces.enrollment import EnrollmentRepository
from app.application.schemas.child import DailyUpdateCreateRequest
from app.domain.entities.child import Attendance, DailyUpdate
from app.domain.entities.enrollment import EnrollmentStatus
from app.domain.entities.user_context import Role, UserContext


class AttendanceService:

    def __init__(
        self,
        attendance_repository: AttendanceRepository,
        enrollment_repository: EnrollmentRepository,
        child_repository: ChildRepository,
    ):
        self.attendance_repository = attendance_repository
        self.enrollment_repository = enrollment_repository
        self.child_repository = child_repository

    @staticmethod
    def _require_staff_access(
        user: UserContext,
        organization_id: str,
    ) -> None:
        if user.role != Role.DAYCARE_STAFF:
            raise PermissionError(
                "Daycare staff access required"
            )

        if (
            organization_id not in user.organization_ids
            and user.organization_id != organization_id
        ):
            raise PermissionError(
                "You do not have access to this daycare"
            )

    def check_in(
        self,
        user: UserContext,
        enrollment_id: str,
    ) -> Attendance:
        if user.role != Role.DAYCARE_STAFF:
            raise PermissionError(
                "Daycare staff access required"
            )

        enrollment = self.enrollment_repository.get_by_id(
            enrollment_id
        )

        if enrollment is None:
            raise LookupError("Enrollment not found")

        self._require_staff_access(
            user,
            enrollment.daycare_organization_id,
        )

        if enrollment.status != EnrollmentStatus.APPROVED:
            raise ValueError(
                "Only approved enrollments can record attendance"
            )

        child = self.child_repository.get(enrollment.child_id)

        if child is None:
            raise LookupError("Child record not found")

        if (
            child.daycare_organization_id
            != enrollment.daycare_organization_id
        ):
            raise ValueError(
                "Child is not currently assigned to this daycare"
            )

        now = datetime.now(timezone.utc)
        local_date = now.astimezone(
            ZoneInfo("Asia/Dhaka")
        ).date()

        attendance = Attendance(
            id=str(uuid4()),
            enrollment_id=enrollment.id,
            attendance_date=local_date,
            check_in_at=now,
            check_out_at=None,
            recorded_by=user.user_id,
        )

        return self.attendance_repository.create_check_in(
            attendance
        )

    def check_out(
        self,
        user: UserContext,
        attendance_id: str,
    ) -> Attendance:
        if user.role != Role.DAYCARE_STAFF:
            raise PermissionError(
                "Daycare staff access required"
            )

        attendance = self.attendance_repository.get_by_id(
            attendance_id
        )

        if attendance is None:
            raise LookupError("Attendance record not found")

        enrollment = self.enrollment_repository.get_by_id(
            attendance.enrollment_id
        )

        if enrollment is None:
            raise LookupError("Enrollment record not found")

        self._require_staff_access(
            user,
            enrollment.daycare_organization_id,
        )

        if attendance.check_out_at is not None:
            raise ValueError(
                "This attendance record is already checked out"
            )

        updated = self.attendance_repository.check_out(
            attendance_id,
            datetime.now(timezone.utc),
        )

        if updated is None:
            raise ValueError(
                "Could not check out; the record may already be closed"
            )

        return updated

    def view_attendance(
        self,
        user: UserContext,
        child_id: str,
    ) -> list[Attendance]:
        child = self.child_repository.get(child_id)

        if child is None:
            raise LookupError("Child record not found")

        if user.role == Role.PARENT_GUARDIAN:
            if child.parent_id != user.user_id:
                raise PermissionError(
                    "You do not have access to this child's attendance"
                )

            return self.attendance_repository.list_for_child(
                child_id
            )

        if user.role == Role.DAYCARE_STAFF:
            organization_id = child.daycare_organization_id

            if organization_id is None:
                raise ValueError(
                    "Child is not currently enrolled at a daycare"
                )

            self._require_staff_access(
                user,
                organization_id,
            )

            if not self.attendance_repository.has_approved_enrollment(
                child_id,
                organization_id,
            ):
                raise ValueError(
                    "An approved daycare enrollment is required"
                )

            return self.attendance_repository.list_for_child(
                child_id,
                organization_id,
            )

        raise PermissionError(
            "You do not have permission to view attendance"
        )

    def add_daily_update(
        self,
        user: UserContext,
        child_id: str,
        request: DailyUpdateCreateRequest,
    ) -> DailyUpdate:
        if user.role != Role.DAYCARE_STAFF:
            raise PermissionError(
                "Daycare staff access required"
            )

        child = self.child_repository.get(child_id)

        if child is None:
            raise LookupError("Child record not found")

        organization_id = child.daycare_organization_id

        if organization_id is None:
            raise ValueError(
                "Child is not currently enrolled at a daycare"
            )

        self._require_staff_access(
            user,
            organization_id,
        )

        if not self.attendance_repository.has_approved_enrollment(
            child_id,
            organization_id,
        ):
            raise ValueError(
                "An approved daycare enrollment is required"
            )

        update = DailyUpdate(
            id=str(uuid4()),
            child_id=child_id,
            daycare_organization_id=organization_id,
            update_date=datetime.now(
                ZoneInfo("Asia/Dhaka")
            ).date(),
            notes=request.notes,
            recorded_by=user.user_id,
            created_at=datetime.now(timezone.utc),
        )

        return self.attendance_repository.create_daily_update(
            update
        )

    def view_daily_updates(
        self,
        user: UserContext,
        child_id: str,
    ) -> list[DailyUpdate]:
        child = self.child_repository.get(child_id)

        if child is None:
            raise LookupError("Child record not found")

        if user.role == Role.PARENT_GUARDIAN:
            if child.parent_id != user.user_id:
                raise PermissionError(
                    "You do not have access to this child's daily updates"
                )

            return self.attendance_repository.list_daily_updates(
                child_id
            )

        if user.role == Role.DAYCARE_STAFF:
            organization_id = child.daycare_organization_id

            if organization_id is None:
                raise ValueError(
                    "Child is not currently enrolled at a daycare"
                )

            self._require_staff_access(
                user,
                organization_id,
            )

            if not self.attendance_repository.has_approved_enrollment(
                child_id,
                organization_id,
            ):
                raise ValueError(
                    "An approved daycare enrollment is required"
                )

            return self.attendance_repository.list_daily_updates(
                child_id,
                organization_id,
            )

        raise PermissionError(
            "You do not have permission to view daily updates"
        )