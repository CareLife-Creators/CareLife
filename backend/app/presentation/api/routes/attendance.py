from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.child import (
    AttendanceCheckInRequest,
    AttendanceResponse,
    DailyUpdateCreateRequest,
    DailyUpdateResponse,
)
from app.application.use_cases.attendance import AttendanceService
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import require_role
from app.presentation.api.dependencies.child import get_attendance_service


router = APIRouter(
    prefix="/daycare",
    tags=["Daycare Attendance and Daily Updates"],
)


@router.post(
    "/attendance/check-in",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED,
)
def check_in(
    request: AttendanceCheckInRequest,
    current_user: UserContext = Depends(
        require_role(Role.DAYCARE_STAFF)
    ),
    service: AttendanceService = Depends(
        get_attendance_service
    ),
):
    try:
        return service.check_in(
            current_user,
            request.enrollment_id,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post(
    "/attendance/{attendance_id}/check-out",
    response_model=AttendanceResponse,
)
def check_out(
    attendance_id: str,
    current_user: UserContext = Depends(
        require_role(Role.DAYCARE_STAFF)
    ),
    service: AttendanceService = Depends(
        get_attendance_service
    ),
):
    try:
        return service.check_out(
            current_user,
            attendance_id,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/children/{child_id}/attendance",
    response_model=list[AttendanceResponse],
)
def view_attendance(
    child_id: str,
    current_user: UserContext = Depends(
        require_role(
            Role.PARENT_GUARDIAN,
            Role.DAYCARE_STAFF,
        )
    ),
    service: AttendanceService = Depends(
        get_attendance_service
    ),
):
    try:
        return service.view_attendance(
            current_user,
            child_id,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post(
    "/children/{child_id}/daily-updates",
    response_model=DailyUpdateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_daily_update(
    child_id: str,
    request: DailyUpdateCreateRequest,
    current_user: UserContext = Depends(
        require_role(Role.DAYCARE_STAFF)
    ),
    service: AttendanceService = Depends(
        get_attendance_service
    ),
):
    try:
        return service.add_daily_update(
            current_user,
            child_id,
            request,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/children/{child_id}/daily-updates",
    response_model=list[DailyUpdateResponse],
)
def view_daily_updates(
    child_id: str,
    current_user: UserContext = Depends(
        require_role(
            Role.PARENT_GUARDIAN,
            Role.DAYCARE_STAFF,
        )
    ),
    service: AttendanceService = Depends(
        get_attendance_service
    ),
):
    try:
        return service.view_daily_updates(
            current_user,
            child_id,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc