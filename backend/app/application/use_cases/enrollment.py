from datetime import datetime, timezone
from uuid import uuid4

from app.application.interfaces.child import (
    ChildRepository,
)
from app.application.interfaces.enrollment import (
    EnrollmentRepository,
)
from app.application.interfaces.organization import (
    OrganizationRepository,
)
from app.application.schemas.enrollment import (
    EnrollmentCreateRequest,
)
from app.domain.entities.enrollment import (
    Enrollment,
    EnrollmentStatus,
)
from app.domain.entities.user_context import (
    Role,
    UserContext,
)


class EnrollmentService:

    def __init__(
        self,
        enrollment_repository: EnrollmentRepository,
        child_repository: ChildRepository,
        organization_repository: OrganizationRepository,
    ):
        self.enrollment_repository = (
            enrollment_repository
        )
        self.child_repository = (
            child_repository
        )
        self.organization_repository = (
            organization_repository
        )

    @staticmethod
    def _organization_access(
        user: UserContext,
        organization_id: str,
    ) -> bool:
        return (
            organization_id in user.organization_ids
            or user.organization_id == organization_id
        )

    def create(
        self,
        user: UserContext,
        request: EnrollmentCreateRequest,
    ) -> Enrollment:

        if user.role != Role.PARENT_GUARDIAN:
            raise PermissionError(
                "Parent or guardian access required"
            )

        child = self.child_repository.get(
            request.child_id
        )

        if child is None:
            raise ValueError(
                "Child record not found"
            )

        if child.parent_id != user.user_id:
            raise PermissionError(
                "You do not have access to this child record"
            )

        daycare = (
            self.organization_repository.get_public_daycare(
                request.daycare_organization_id
            )
        )

        if daycare is None:
            raise ValueError(
                "Verified daycare not found"
            )

        now = datetime.now(timezone.utc)

        enrollment = Enrollment(
            id=str(uuid4()),
            child_id=request.child_id,
            daycare_organization_id=(
                request.daycare_organization_id
            ),
            status=EnrollmentStatus.PENDING,
            requested_at=now,
            reviewed_at=None,
            reviewed_by=None,
            cancelled_at=None,
            decision_message=None,
        )

        return self.enrollment_repository.create(
            enrollment
        )

    def list_for_parent(
        self,
        user: UserContext,
    ) -> list[Enrollment]:

        if user.role != Role.PARENT_GUARDIAN:
            raise PermissionError(
                "Parent or guardian access required"
            )

        return self.enrollment_repository.list_by_parent(
            user.user_id
        )

    def list_pending_for_staff(
        self,
        user: UserContext,
    ) -> list[Enrollment]:

        if user.role != Role.DAYCARE_STAFF:
            raise PermissionError(
                "Daycare staff access required"
            )

        organization_ids = list(
            user.organization_ids
        )

        if (
            user.organization_id
            and user.organization_id not in organization_ids
        ):
            organization_ids.append(
                user.organization_id
            )

        enrollments: list[Enrollment] = []

        for organization_id in organization_ids:
            daycare = (
                self.organization_repository.get_public_daycare(
                    organization_id
                )
            )

            if daycare is None:
                continue

            enrollments.extend(
                self.enrollment_repository.list_pending_by_daycare(
                    organization_id
                )
            )

        return enrollments

    def get(
        self,
        user: UserContext,
        enrollment_id: str,
    ) -> Enrollment:

        enrollment = (
            self.enrollment_repository.get_by_id(
                enrollment_id
            )
        )

        if enrollment is None:
            raise ValueError(
                "Enrollment record not found"
            )

        child = self.child_repository.get(
            enrollment.child_id
        )

        if child is None:
            raise ValueError(
                "Child record not found"
            )

        if user.role == Role.PARENT_GUARDIAN:

            if child.parent_id != user.user_id:
                raise PermissionError(
                    "You do not have access to this enrollment"
                )

            return enrollment

        if user.role == Role.DAYCARE_STAFF:

            if not self._organization_access(
                user,
                enrollment.daycare_organization_id,
            ):
                raise PermissionError(
                    "You do not have access to this enrollment"
                )

            return enrollment

        raise PermissionError(
            "You do not have permission to access this enrollment"
        )

    def review(
        self,
        user: UserContext,
        enrollment_id: str,
        status: EnrollmentStatus,
        message: str | None = None,
    ) -> Enrollment:

        if user.role != Role.DAYCARE_STAFF:
            raise PermissionError(
                "Daycare staff access required"
            )

        enrollment = (
            self.enrollment_repository.get_by_id(
                enrollment_id
            )
        )

        if enrollment is None:
            raise ValueError(
                "Enrollment record not found"
            )

        if not self._organization_access(
            user,
            enrollment.daycare_organization_id,
        ):
            raise PermissionError(
                "You do not have access to this enrollment"
            )

        if status not in (
            EnrollmentStatus.APPROVED,
            EnrollmentStatus.REJECTED,
            EnrollmentStatus.WAITLISTED,
        ):
            raise ValueError(
                "Invalid enrollment review status"
            )

        updated = self.enrollment_repository.review(
            enrollment_id,
            status,
            user.user_id,
            message,
        )

        if updated is None:
            raise ValueError(
                "Enrollment record not found"
            )

        return updated

    def cancel(
        self,
        user: UserContext,
        enrollment_id: str,
    ) -> Enrollment:

        if user.role != Role.PARENT_GUARDIAN:
            raise PermissionError(
                "Parent or guardian access required"
            )

        enrollment = (
            self.enrollment_repository.get_by_id(
                enrollment_id
            )
        )

        if enrollment is None:
            raise ValueError(
                "Enrollment record not found"
            )

        child = self.child_repository.get(
            enrollment.child_id
        )

        if child is None:
            raise ValueError(
                "Child record not found"
            )

        if child.parent_id != user.user_id:
            raise PermissionError(
                "You do not have access to this enrollment"
            )

        updated = (
            self.enrollment_repository.cancel(
                enrollment_id
            )
        )

        if updated is None:
            raise ValueError(
                "Enrollment record not found"
            )

        return updated