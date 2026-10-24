from fastapi import APIRouter, Depends, HTTPException, status

from app.application.schemas.caregiver_booking import (
    CaregiverAppointmentCreateRequest,
    CaregiverAppointmentDecisionRequest,
    CaregiverAppointmentResponse,
    CaregiverAvailabilityCreateRequest,
    CaregiverAvailabilityResponse,
)
from app.application.use_cases.caregiver_booking import (
    CaregiverBookingService,
)
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import (
    require_role,
)
from app.presentation.api.dependencies.caregiver_booking import (
    get_caregiver_booking_service,
)


router = APIRouter(tags=["Independent Caregiver Booking"])


@router.post(
    "/caregivers/me/availability",
    response_model=CaregiverAvailabilityResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_availability(
    request: CaregiverAvailabilityCreateRequest,
    current_user: UserContext = Depends(
        require_role(Role.INDEPENDENT_CAREGIVER)
    ),
    service: CaregiverBookingService = Depends(
        get_caregiver_booking_service
    ),
):
    try:
        slot = service.create_availability(
            current_user,
            request,
        )
        return CaregiverAvailabilityResponse.from_entity(slot)
    except PermissionError as exc:
        raise HTTPException(403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, detail=str(exc)) from exc


@router.get(
    "/caregivers/me/availability",
    response_model=list[CaregiverAvailabilityResponse],
)
def list_my_availability(
    current_user: UserContext = Depends(
        require_role(Role.INDEPENDENT_CAREGIVER)
    ),
    service: CaregiverBookingService = Depends(
        get_caregiver_booking_service
    ),
):
    try:
        slots = service.list_my_availability(current_user)
        return [
            CaregiverAvailabilityResponse.from_entity(slot)
            for slot in slots
        ]
    except PermissionError as exc:
        raise HTTPException(403, detail=str(exc)) from exc


@router.get(
    "/caregivers/{caregiver_id}/availability",
    response_model=list[CaregiverAvailabilityResponse],
)
def list_public_availability(
    caregiver_id: str,
    service: CaregiverBookingService = Depends(
        get_caregiver_booking_service
    ),
):
    try:
        slots = service.list_public_availability(caregiver_id)
        return [
            CaregiverAvailabilityResponse.from_entity(slot)
            for slot in slots
        ]
    except LookupError as exc:
        raise HTTPException(404, detail=str(exc)) from exc


@router.post(
    "/appointments",
    response_model=CaregiverAppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
    request: CaregiverAppointmentCreateRequest,
    current_user: UserContext = Depends(
        require_role(
            Role.PARENT_GUARDIAN,
            Role.FAMILY_REPRESENTATIVE,
        )
    ),
    service: CaregiverBookingService = Depends(
        get_caregiver_booking_service
    ),
):
    try:
        appointment = service.create_appointment(
            current_user,
            request,
        )
        return CaregiverAppointmentResponse.from_entity(
            appointment
        )
    except PermissionError as exc:
        raise HTTPException(403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, detail=str(exc)) from exc


@router.get(
    "/appointments/me",
    response_model=list[CaregiverAppointmentResponse],
)
def list_my_appointments(
    current_user: UserContext = Depends(
        require_role(
            Role.PARENT_GUARDIAN,
            Role.FAMILY_REPRESENTATIVE,
            Role.INDEPENDENT_CAREGIVER,
        )
    ),
    service: CaregiverBookingService = Depends(
        get_caregiver_booking_service
    ),
):
    try:
        appointments = service.list_my_appointments(current_user)
        return [
            CaregiverAppointmentResponse.from_entity(item)
            for item in appointments
        ]
    except PermissionError as exc:
        raise HTTPException(403, detail=str(exc)) from exc


@router.get(
    "/appointments/{appointment_id}",
    response_model=CaregiverAppointmentResponse,
)
def get_appointment(
    appointment_id: str,
    current_user: UserContext = Depends(
        require_role(
            Role.PARENT_GUARDIAN,
            Role.FAMILY_REPRESENTATIVE,
            Role.INDEPENDENT_CAREGIVER,
        )
    ),
    service: CaregiverBookingService = Depends(
        get_caregiver_booking_service
    ),
):
    try:
        appointment = service.get_appointment(
            current_user,
            appointment_id,
        )
        return CaregiverAppointmentResponse.from_entity(
            appointment
        )
    except LookupError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(403, detail=str(exc)) from exc


@router.post(
    "/appointments/{appointment_id}/decision",
    response_model=CaregiverAppointmentResponse,
)
def decide_appointment(
    appointment_id: str,
    request: CaregiverAppointmentDecisionRequest,
    current_user: UserContext = Depends(
        require_role(Role.INDEPENDENT_CAREGIVER)
    ),
    service: CaregiverBookingService = Depends(
        get_caregiver_booking_service
    ),
):
    try:
        appointment = service.decide_appointment(
            current_user,
            appointment_id,
            request,
        )
        return CaregiverAppointmentResponse.from_entity(
            appointment
        )
    except LookupError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, detail=str(exc)) from exc