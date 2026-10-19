from typing import Protocol

from app.domain.entities.elder_care_booking import (
    ElderCareBooking,
    ElderCareBookingStatus,
    ElderCareBookingStatusHistory,
)
from app.domain.entities.user_context import Role


class ElderCareBookingRepository(Protocol):

    def create_booking(
        self,
        requester_user_id: str,
        values: dict[str, object],
    ) -> ElderCareBooking:
        ...

    def get_booking(
        self,
        booking_id: str,
    ) -> ElderCareBooking | None:
        ...

    def list_for_user(
        self,
        user_id: str,
        role: Role,
    ) -> list[ElderCareBooking]:
        ...

    def get_status_history(
        self,
        booking_id: str,
    ) -> list[ElderCareBookingStatusHistory]:
        ...

    def is_care_home_staff(
        self,
        user_id: str,
        organization_id: str,
    ) -> bool:
        ...

    def is_approved_elder_care_caregiver(
        self,
        user_id: str,
    ) -> bool:
        ...

    def transition_booking(
        self,
        booking_id: str,
        actor_user_id: str,
        new_status: ElderCareBookingStatus,
        allowed_current_statuses: tuple[
            ElderCareBookingStatus, ...
        ],
        note: str | None,
    ) -> ElderCareBooking:
        ...