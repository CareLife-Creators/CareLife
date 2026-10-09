import unittest
from datetime import date, datetime, timezone
from unittest.mock import Mock

from app.application.schemas.enrollment import EnrollmentCreateRequest
from app.application.use_cases.enrollment import EnrollmentService
from app.domain.entities.child import Child
from app.domain.entities.enrollment import Enrollment, EnrollmentStatus
from app.domain.entities.user_context import Role, UserContext


def make_child(parent_id: str = "parent-1") -> Child:
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
        daycare_organization_id=None,
        created_at=now,
        updated_at=now,
    )


def make_enrollment(status: EnrollmentStatus = EnrollmentStatus.PENDING) -> Enrollment:
    return Enrollment(
        id="enrollment-1",
        child_id="child-1",
        daycare_organization_id="daycare-1",
        status=status,
        requested_at=datetime.now(timezone.utc),
    )


class EnrollmentServiceTests(unittest.TestCase):
    def setUp(self):
        self.enrollment_repository = Mock()
        self.child_repository = Mock()
        self.organization_repository = Mock()
        self.service = EnrollmentService(
            enrollment_repository=self.enrollment_repository,
            child_repository=self.child_repository,
            organization_repository=self.organization_repository,
        )
        self.child_repository.get.return_value = make_child()
        self.organization_repository.get_public_daycare.return_value = object()
        self.enrollment_repository.create.side_effect = lambda item: item
        self.parent = UserContext(user_id="parent-1", role=Role.PARENT_GUARDIAN)
        self.staff = UserContext(
            user_id="staff-1",
            role=Role.DAYCARE_STAFF,
            organization_id="daycare-1",
        )

    def test_parent_can_create_pending_enrollment_for_own_child(self):
        result = self.service.create(
            self.parent,
            EnrollmentCreateRequest(
                child_id="child-1",
                daycare_organization_id="daycare-1",
            ),
        )

        self.assertEqual(result.status, EnrollmentStatus.PENDING)
        self.assertEqual(result.child_id, "child-1")
        self.enrollment_repository.create.assert_called_once()

    def test_parent_cannot_enroll_another_parents_child(self):
        self.child_repository.get.return_value = make_child(parent_id="different-parent")

        with self.assertRaises(PermissionError):
            self.service.create(
                self.parent,
                EnrollmentCreateRequest(
                    child_id="child-1",
                    daycare_organization_id="daycare-1",
                ),
            )

        self.enrollment_repository.create.assert_not_called()

    def test_staff_cannot_create_parent_enrollment(self):
        with self.assertRaises(PermissionError):
            self.service.create(
                self.staff,
                EnrollmentCreateRequest(
                    child_id="child-1",
                    daycare_organization_id="daycare-1",
                ),
            )

        self.enrollment_repository.create.assert_not_called()

    def test_parent_cannot_view_another_parents_enrollment(self):
        self.enrollment_repository.get_by_id.return_value = make_enrollment()
        self.child_repository.get.return_value = make_child(parent_id="different-parent")

        with self.assertRaises(PermissionError):
            self.service.get(self.parent, "enrollment-1")

    def test_staff_cannot_review_another_daycare_enrollment(self):
        self.enrollment_repository.get_by_id.return_value = make_enrollment()
        other_staff = UserContext(
            user_id="staff-2",
            role=Role.DAYCARE_STAFF,
            organization_id="daycare-2",
        )

        with self.assertRaises(PermissionError):
            self.service.review(
                other_staff,
                "enrollment-1",
                EnrollmentStatus.APPROVED,
            )

        self.enrollment_repository.review.assert_not_called()

    def test_public_daycare_must_exist_before_enrollment(self):
        self.organization_repository.get_public_daycare.return_value = None

        with self.assertRaisesRegex(ValueError, "Verified daycare"):
            self.service.create(
                self.parent,
                EnrollmentCreateRequest(
                    child_id="child-1",
                    daycare_organization_id="daycare-1",
                ),
            )

        self.enrollment_repository.create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
