from typing import Protocol

from app.domain.entities.caregiver_booking import (
    CaregiverAppointment,
    CaregiverAppointmentStatus,
    CaregiverAvailability,
)


class CaregiverBookingRepository(Protocol):

    def create_availability(
        self,
        caregiver_user_id: str,
        starts_at,
        ends_at,
    ) -> CaregiverAvailability:
        ...

    def list_availability_for_caregiver(
        self,
        caregiver_user_id: str,
    ) -> list[CaregiverAvailability]:
        ...

    def list_public_availability(
        self,
        caregiver_user_id: str,
    ) -> list[CaregiverAvailability]:
        ...

    def create_appointment(
        self,
        requester_user_id: str,
        availability_id: str,
        message: str | None,
    ) -> CaregiverAppointment:
        ...

    def get_appointment(
        self,
        appointment_id: str,
    ) -> CaregiverAppointment | None:
        ...

    def list_for_requester(
        self,
        requester_user_id: str,
    ) -> list[CaregiverAppointment]:
        ...

    def list_for_caregiver(
        self,
        caregiver_user_id: str,
    ) -> list[CaregiverAppointment]:
        ...

    def decide_appointment(
        self,
        appointment_id: str,
        caregiver_user_id: str,
        status: CaregiverAppointmentStatus,
        message: str | None,
    ) -> CaregiverAppointment | None:
        ...