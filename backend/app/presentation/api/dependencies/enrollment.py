from app.application.use_cases.enrollment import (
    EnrollmentService,
)
from app.infrastructure.repositories.child import (
    PostgresChildRepository,
)
from app.infrastructure.repositories.enrollment import (
    PostgresEnrollmentRepository,
)
from app.infrastructure.repositories.organization_repository import (
    PostgresOrganizationRepository,
)


def get_enrollment_service() -> EnrollmentService:
    return EnrollmentService(
        enrollment_repository=(
            PostgresEnrollmentRepository()
        ),
        child_repository=(
            PostgresChildRepository()
        ),
        organization_repository=(
            PostgresOrganizationRepository()
        ),
    )