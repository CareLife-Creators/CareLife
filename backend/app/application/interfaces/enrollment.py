from typing import Protocol

from app.domain.entities.enrollment import (
    Enrollment,
    EnrollmentStatus,
)


class EnrollmentRepository(Protocol):

    def create(
        self,
        enrollment: Enrollment,
    ) -> Enrollment:
        ...

    def get_by_id(
        self,
        enrollment_id: str,
    ) -> Enrollment | None:
        ...

    def list_by_parent(
        self,
        parent_id: str,
    ) -> list[Enrollment]:
        ...

    def list_pending_by_daycare(
        self,
        organization_id: str,
    ) -> list[Enrollment]:
        ...

    def review(
        self,
        enrollment_id: str,
        status: EnrollmentStatus,
        reviewer_id: str,
        message: str | None = None,
    ) -> Enrollment | None:
        ...

    def cancel(
        self,
        enrollment_id: str,
    ) -> Enrollment | None:
        ...