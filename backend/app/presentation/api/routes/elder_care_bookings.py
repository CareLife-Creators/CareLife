from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.elder_care_booking import (
    ElderCareBookingCreateRequest,
    ElderCareBookingDecisionRequest,
    ElderCareBookingNoteRequest,
    ElderCareBookingResponse,
    ElderCareBookingStatusHistoryResponse,
)
from app.application.use_cases.elder_care_booking import (
    ElderCareBookingService,
)
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import (
    require_role,
)
from app.presentation.api.dependencies.elder_care_booking import (
    get_elder_care_booking_service,
)


router = APIRouter(
    prefix="/elder-care",
    tags=["Elder-Care Booking"],
)


def _raise_http_error(exc: Exception) -> None:
    if isinstance(exc, PermissionError):
        code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, LookupError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ValueError):
        code = status.HTTP_409_CONFLICT
    else:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR

    raise HTTPException(
        status_code=code,
        detail=str(exc),
    ) from exc


@router.post(
    "/bookings",
    response_model=ElderCareBookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    request: ElderCareBookingCreateRequest,
    current_user: UserContext = Depends(
        require_role(
            Role.FAMILY_REPRESENTATIVE,
            Role.PARENT_GUARDIAN,
        )
    ),
    service: ElderCareBookingService = Depends(
        get_elder_care_booking_service
    ),
) -> ElderCareBookingResponse:
    try:
        booking = service.create_booking(
            current_user,
            request,
        )
        return ElderCareBookingResponse.from_entity(booking)

    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.get(
    "/bookings",
    response_model=list[ElderCareBookingResponse],
)
def list_bookings(
    current_user: UserContext = Depends(
        require_role(
            Role.FAMILY_REPRESENTATIVE,
            Role.PARENT_GUARDIAN,
            Role.INDEPENDENT_CAREGIVER,
            Role.CARE_HOME_STAFF,
            Role.CARELIFE_ADMIN,
        )
    ),
    service: ElderCareBookingService = Depends(
        get_elder_care_booking_service
    ),
) -> list[ElderCareBookingResponse]:
    try:
        bookings = service.list_bookings(current_user)

        return [
            ElderCareBookingResponse.from_entity(booking)
            for booking in bookings
        ]

    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.get(
    "/bookings/{booking_id}",
    response_model=ElderCareBookingResponse,
)
def get_booking(
    booking_id: str,
    current_user: UserContext = Depends(
        require_role(
            Role.FAMILY_REPRESENTATIVE,
            Role.PARENT_GUARDIAN,
            Role.INDEPENDENT_CAREGIVER,
            Role.CARE_HOME_STAFF,
            Role.CARELIFE_ADMIN,
        )
    ),
    service: ElderCareBookingService = Depends(
        get_elder_care_booking_service
    ),
) -> ElderCareBookingResponse:
    try:
        booking = service.get_booking(current_user, booking_id)

        return ElderCareBookingResponse.from_entity(booking)

    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.get(
    "/bookings/{booking_id}/history",
    response_model=list[ElderCareBookingStatusHistoryResponse],
)
def get_booking_history(
    booking_id: str,
    current_user: UserContext = Depends(
        require_role(
            Role.FAMILY_REPRESENTATIVE,
            Role.PARENT_GUARDIAN,
            Role.INDEPENDENT_CAREGIVER,
            Role.CARE_HOME_STAFF,
            Role.CARELIFE_ADMIN,
        )
    ),
    service: ElderCareBookingService = Depends(
        get_elder_care_booking_service
    ),
) -> list[ElderCareBookingStatusHistoryResponse]:
    try:
        history = service.get_status_history(
            current_user,
            booking_id,
        )

        return [
            ElderCareBookingStatusHistoryResponse.from_entity(item)
            for item in history
        ]

    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.post(
    "/bookings/{booking_id}/decision",
    response_model=ElderCareBookingResponse,
)
def decide_booking(
    booking_id: str,
    request: ElderCareBookingDecisionRequest,
    current_user: UserContext = Depends(
        require_role(
            Role.INDEPENDENT_CAREGIVER,
            Role.CARE_HOME_STAFF,
        )
    ),
    service: ElderCareBookingService = Depends(
        get_elder_care_booking_service
    ),
) -> ElderCareBookingResponse:
    try:
        booking = service.decide_booking(
            current_user,
            booking_id,
            request,
        )

        return ElderCareBookingResponse.from_entity(booking)

    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.post(
    "/bookings/{booking_id}/cancel",
    response_model=ElderCareBookingResponse,
)
def cancel_booking(
    booking_id: str,
    request: ElderCareBookingNoteRequest,
    current_user: UserContext = Depends(
        require_role(
            Role.FAMILY_REPRESENTATIVE,
            Role.PARENT_GUARDIAN,
        )
    ),
    service: ElderCareBookingService = Depends(
        get_elder_care_booking_service
    ),
) -> ElderCareBookingResponse:
    try:
        booking = service.cancel_booking(
            current_user,
            booking_id,
            request,
        )

        return ElderCareBookingResponse.from_entity(booking)

    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.post(
    "/bookings/{booking_id}/complete",
    response_model=ElderCareBookingResponse,
)
def complete_booking(
    booking_id: str,
    request: ElderCareBookingNoteRequest,
    current_user: UserContext = Depends(
        require_role(
            Role.INDEPENDENT_CAREGIVER,
            Role.CARE_HOME_STAFF,
        )
    ),
    service: ElderCareBookingService = Depends(
        get_elder_care_booking_service
    ),
) -> ElderCareBookingResponse:
    try:
        booking = service.complete_booking(
            current_user,
            booking_id,
            request,
        )

        return ElderCareBookingResponse.from_entity(booking)

    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)