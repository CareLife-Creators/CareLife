from datetime import datetime, timezone

from app.application.interfaces.caregiver_booking import (
    CaregiverBookingRepository,
)
from app.application.schemas.caregiver_booking import (
    CaregiverAppointmentCreateRequest,
    CaregiverAppointmentDecisionRequest,
    CaregiverAvailabilityCreateRequest,
)
from app.domain.entities.caregiver_booking import (
    CaregiverAppointment,
    CaregiverAppointmentStatus,
    CaregiverAvailability,
)
from app.domain.entities.user_context import Role, UserContext


class CaregiverBookingService:

    def __init__(
        self,
        repository: CaregiverBookingRepository,
    ):
        self.repository = repository

    @staticmethod
    def _require_caregiver(user: UserContext) -> None:
        if user.role != Role.INDEPENDENT_CAREGIVER:
            raise PermissionError(
                "Independent caregiver access required."
            )

    @staticmethod
    def _require_requester(user: UserContext) -> None:
        if user.role not in (
            Role.PARENT_GUARDIAN,
            Role.FAMILY_REPRESENTATIVE,
        ):
            raise PermissionError(
                "Parent or family representative access required."
            )

    def create_availability(
        self,
        user: UserContext,
        request: CaregiverAvailabilityCreateRequest,
    ) -> CaregiverAvailability:
        self._require_caregiver(user)

        now = datetime.now(timezone.utc)

        if request.starts_at <= now:
            raise ValueError(
                "Availability must start in the future."
            )

        if request.ends_at <= request.starts_at:
            raise ValueError(
                "End time must be later than start time."
            )

        return self.repository.create_availability(
            caregiver_user_id=user.user_id,
            starts_at=request.starts_at,
            ends_at=request.ends_at,
        )

    def list_my_availability(
        self,
        user: UserContext,
    ) -> list[CaregiverAvailability]:
        self._require_caregiver(user)

        return self.repository.list_availability_for_caregiver(
            user.user_id
        )

    def list_public_availability(
        self,
        caregiver_id: str,
    ) -> list[CaregiverAvailability]:
        return self.repository.list_public_availability(
            caregiver_id
        )

    def create_appointment(
        self,
        user: UserContext,
        request: CaregiverAppointmentCreateRequest,
    ) -> CaregiverAppointment:
        self._require_requester(user)

        return self.repository.create_appointment(
            requester_user_id=user.user_id,
            availability_id=request.availability_id,
            message=request.message,
        )

    def list_my_appointments(
        self,
        user: UserContext,
    ) -> list[CaregiverAppointment]:
        if user.role in (
            Role.PARENT_GUARDIAN,
            Role.FAMILY_REPRESENTATIVE,
        ):
            return self.repository.list_for_requester(
                user.user_id
            )

        if user.role == Role.INDEPENDENT_CAREGIVER:
            return self.repository.list_for_caregiver(
                user.user_id
            )

        raise PermissionError(
            "You do not have permission to view these appointments."
        )

    def get_appointment(
        self,
        user: UserContext,
        appointment_id: str,
    ) -> CaregiverAppointment:
        if user.role not in (
            Role.PARENT_GUARDIAN,
            Role.FAMILY_REPRESENTATIVE,
            Role.INDEPENDENT_CAREGIVER,
        ):
            raise PermissionError(
                "You do not have permission to view this appointment."
            )

        appointment = self.repository.get_appointment(
            appointment_id
        )

        if appointment is None:
            raise LookupError("Appointment not found.")

        if user.user_id not in (
            appointment.requester_user_id,
            appointment.caregiver_user_id,
        ):
            raise PermissionError(
                "You do not have access to this appointment."
            )

        return appointment

    def decide_appointment(
        self,
        user: UserContext,
        appointment_id: str,
        request: CaregiverAppointmentDecisionRequest,
    ) -> CaregiverAppointment:
        self._require_caregiver(user)

        appointment = self.repository.get_appointment(
            appointment_id
        )

        if appointment is None:
            raise LookupError("Appointment not found.")

        if appointment.caregiver_user_id != user.user_id:
            raise PermissionError(
                "You cannot review another caregiver's appointment."
            )

        if (
            appointment.status
            != CaregiverAppointmentStatus.REQUESTED
        ):
            raise ValueError(
                "Only requested appointments can be reviewed."
            )

        status = CaregiverAppointmentStatus(request.status)

        updated = self.repository.decide_appointment(
            appointment_id=appointment_id,
            caregiver_user_id=user.user_id,
            status=status,
            message=request.message,
        )

        if updated is None:
            raise ValueError(
                "The appointment has already been reviewed."
            )

        return updated