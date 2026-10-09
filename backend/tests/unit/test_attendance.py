import unittest
from datetime import date, datetime, timezone
from unittest.mock import Mock

from app.application.schemas.child import DailyUpdateCreateRequest
from app.application.use_cases.attendance import AttendanceService
from app.domain.entities.child import Attendance, Child, DailyUpdate
from app.domain.entities.enrollment import Enrollment, EnrollmentStatus
from app.domain.entities.user_context import Role, UserContext


def make_child(parent_id: str = "parent-1", daycare_id: str | None = "daycare-1") -> Child:
    now = datetime.now(timezone.utc)
    return Child(
        id="child-1",
        parent_id=parent_id,
        full_name="Test Child",
        date_of_birth=date(2019, 5, 1),
        gender=None,
        allergies=None,
        medical_notes=None,
        orphanage_organization_id=None,
        daycare_organization_id=daycare_id,
        created_at=now,
        updated_at=now,
    )


def make_enrollment(status: EnrollmentStatus = EnrollmentStatus.APPROVED) -> Enrollment:
    return Enrollment(
        id="enrollment-1",
        child_id="child-1",
        daycare_organization_id="daycare-1",
        status=status,
        requested_at=datetime.now(timezone.utc),
    )


class AttendanceServiceTests(unittest.TestCase):
    def setUp(self):
        self.attendance_repository = Mock()
        self.enrollment_repository = Mock()
        self.child_repository = Mock()
        self.service = AttendanceService(
            attendance_repository=self.attendance_repository,
            enrollment_repository=self.enrollment_repository,
            child_repository=self.child_repository,
        )
        self.child_repository.get.return_value = make_child()
        self.enrollment_repository.get_by_id.return_value = make_enrollment()
        self.attendance_repository.create_check_in.side_effect = lambda record: record
        self.attendance_repository.create_daily_update.side_effect = lambda record: record
        self.attendance_repository.has_approved_enrollment.return_value = True
        self.staff = UserContext(
            user_id="staff-1",
            role=Role.DAYCARE_STAFF,
            organization_id="daycare-1",
        )
        self.parent = UserContext(
            user_id="parent-1",
            role=Role.PARENT_GUARDIAN,
        )

    def test_daycare_staff_can_check_in_approved_enrollment(self):
        result = self.service.check_in(self.staff, "enrollment-1")

        self.assertEqual(result.enrollment_id, "enrollment-1")
        self.assertEqual(result.recorded_by, "staff-1")
        self.assertIsNone(result.check_out_at)
        self.attendance_repository.create_check_in.assert_called_once()

    def test_pending_enrollment_cannot_check_in(self):
        self.enrollment_repository.get_by_id.return_value = make_enrollment(
            EnrollmentStatus.PENDING
        )

        with self.assertRaisesRegex(ValueError, "approved enrollments"):
            self.service.check_in(self.staff, "enrollment-1")

        self.attendance_repository.create_check_in.assert_not_called()

    def test_staff_from_another_daycare_cannot_check_in(self):
        other_staff = UserContext(
            user_id="staff-2",
            role=Role.DAYCARE_STAFF,
            organization_id="daycare-2",
        )

        with self.assertRaises(PermissionError):
            self.service.check_in(other_staff, "enrollment-1")

        self.attendance_repository.create_check_in.assert_not_called()

    def test_parent_cannot_check_in(self):
        with self.assertRaises(PermissionError):
            self.service.check_in(self.parent, "enrollment-1")

        self.attendance_repository.create_check_in.assert_not_called()

    def test_parent_cannot_view_another_child_attendance(self):
        self.child_repository.get.return_value = make_child(parent_id="other-parent")

        with self.assertRaises(PermissionError):
            self.service.view_attendance(self.parent, "child-1")

        self.attendance_repository.list_for_child.assert_not_called()

    def test_staff_can_add_daily_update_for_approved_enrollment(self):
        result = self.service.add_daily_update(
            self.staff,
            "child-1",
            DailyUpdateCreateRequest(notes="Ate lunch and took a nap."),
        )

        self.assertIsInstance(result, DailyUpdate)
        self.assertEqual(result.notes, "Ate lunch and took a nap.")
        self.attendance_repository.create_daily_update.assert_called_once()

    def test_daily_update_requires_approved_enrollment(self):
        self.attendance_repository.has_approved_enrollment.return_value = False

        with self.assertRaisesRegex(ValueError, "approved daycare enrollment"):
            self.service.add_daily_update(
                self.staff,
                "child-1",
                DailyUpdateCreateRequest(notes="Daily note."),
            )

        self.attendance_repository.create_daily_update.assert_not_called()


if __name__ == "__main__":
    unittest.main()
