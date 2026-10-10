from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.application.schemas.enrollment import (
    EnrollmentCreateRequest,
    EnrollmentResponse,
    EnrollmentReviewRequest,
)
from app.application.use_cases.enrollment import (
    EnrollmentService,
)
from app.domain.entities.user_context import (
    Role,
    UserContext,
)
from app.presentation.api.dependencies.authorization import (
    require_role,
)
from app.presentation.api.dependencies.enrollment import (
    get_enrollment_service,
)


router = APIRouter(
    prefix="/enrollments",
    tags=["Daycare Enrollment"],
)


@router.post(
    "",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_enrollment(
    request: EnrollmentCreateRequest,
    current_user: UserContext = Depends(
        require_role(Role.PARENT_GUARDIAN)
    ),
    service: EnrollmentService = Depends(
        get_enrollment_service
    ),
):
    try:
        enrollment = service.create(
            current_user,
            request,
        )

        return EnrollmentResponse.from_entity(
            enrollment
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[EnrollmentResponse],
)
def list_my_enrollments(
    current_user: UserContext = Depends(
        require_role(Role.PARENT_GUARDIAN)
    ),
    service: EnrollmentService = Depends(
        get_enrollment_service
    ),
):
    try:
        enrollments = service.list_for_parent(
            current_user
        )

        return [
            EnrollmentResponse.from_entity(
                enrollment
            )
            for enrollment in enrollments
        ]

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get(
    "/daycare/pending",
    response_model=list[EnrollmentResponse],
)
def list_pending_enrollments(
    current_user: UserContext = Depends(
        require_role(Role.DAYCARE_STAFF)
    ),
    service: EnrollmentService = Depends(
        get_enrollment_service
    ),
):
    try:
        enrollments = (
            service.list_pending_for_staff(
                current_user
            )
        )

        return [
            EnrollmentResponse.from_entity(
                enrollment
            )
            for enrollment in enrollments
        ]

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.get(
    "/{enrollment_id}",
    response_model=EnrollmentResponse,
)
def get_enrollment(
    enrollment_id: str,
    current_user: UserContext = Depends(
        require_role(
            Role.PARENT_GUARDIAN,
            Role.DAYCARE_STAFF,
        )
    ),
    service: EnrollmentService = Depends(
        get_enrollment_service
    ),
):
    try:
        enrollment = service.get(
            current_user,
            enrollment_id,
        )

        return EnrollmentResponse.from_entity(
            enrollment
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.post(
    "/{enrollment_id}/review",
    response_model=EnrollmentResponse,
)
def review_enrollment(
    enrollment_id: str,
    request: EnrollmentReviewRequest,
    current_user: UserContext = Depends(
        require_role(Role.DAYCARE_STAFF)
    ),
    service: EnrollmentService = Depends(
        get_enrollment_service
    ),
):
    try:
        enrollment = service.review(
            current_user,
            enrollment_id,
            request.status,
            request.message,
        )

        return EnrollmentResponse.from_entity(
            enrollment
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.post(
    "/{enrollment_id}/cancel",
    response_model=EnrollmentResponse,
)
def cancel_enrollment(
    enrollment_id: str,
    current_user: UserContext = Depends(
        require_role(Role.PARENT_GUARDIAN)
    ),
    service: EnrollmentService = Depends(
        get_enrollment_service
    ),
):
    try:
        enrollment = service.cancel(
            current_user,
            enrollment_id,
        )

        return EnrollmentResponse.from_entity(
            enrollment
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc