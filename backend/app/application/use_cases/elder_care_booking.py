from datetime import datetime, timezone

from app.application.interfaces.elder_care_booking import (
    ElderCareBookingRepository,
)
from app.application.schemas.elder_care_booking import (
    ElderCareBookingCreateRequest,
    ElderCareBookingDecisionRequest,
    ElderCareBookingNoteRequest,
)
from app.domain.entities.elder_care_booking import (
    ElderCareBooking,
    ElderCareBookingStatus,
    ElderCareBookingStatusHistory,
    ElderCareProviderType,
)
from app.domain.entities.user_context import Role, UserContext


REQUESTER_ROLES = {
    Role.FAMILY_REPRESENTATIVE,
}

VIEWER_ROLES = {
    Role.FAMILY_REPRESENTATIVE,
    Role.INDEPENDENT_CAREGIVER,
    Role.CARE_HOME_STAFF,
    Role.CARELIFE_ADMIN,
}


class ElderCareBookingService:

    def __init__(
        self,
        repository: ElderCareBookingRepository,
    ):
        self.repository = repository

    @staticmethod
    def _require_requester(user: UserContext) -> None:
        if user.role not in REQUESTER_ROLES:
            raise PermissionError(
                "Family representative access is required"
            )

    def create_booking(
        self,
        user: UserContext,
        request: ElderCareBookingCreateRequest,
    ) -> ElderCareBooking:
        self._require_requester(user)

        if request.starts_at <= datetime.now(timezone.utc):
            raise ValueError(
                "A booking must start in the future"
            )

        return self.repository.create_booking(
            requester_user_id=user.user_id,
            values=request.model_dump(),
        )

    def list_bookings(
        self,
        user: UserContext,
    ) -> list[ElderCareBooking]:
        if user.role not in VIEWER_ROLES:
            raise PermissionError(
                "You cannot view elder-care bookings"
            )

        return self.repository.list_for_user(
            user_id=user.user_id,
            role=user.role,
        )

    def _require_read_access(
        self,
        user: UserContext,
        booking: ElderCareBooking,
    ) -> None:
        if user.role == Role.CARELIFE_ADMIN:
            return

        if (
            user.role in REQUESTER_ROLES
            and booking.requester_user_id == user.user_id
        ):
            return

        if (
            user.role == Role.INDEPENDENT_CAREGIVER
            and booking.caregiver_user_id == user.user_id
        ):
            return

        if (
            user.role == Role.CARE_HOME_STAFF
            and self.repository.is_care_home_staff(
                user.user_id,
                booking.resident_organization_id,
            )
        ):
            return

        raise PermissionError(
            "You are not authorized to access this booking"
        )

    def get_booking(
        self,
        user: UserContext,
        booking_id: str,
    ) -> ElderCareBooking:
        if user.role not in VIEWER_ROLES:
            raise PermissionError(
                "You cannot view elder-care bookings"
            )

        booking = self.repository.get_booking(booking_id)

        if booking is None:
            raise LookupError("Elder-care booking not found")

        self._require_read_access(user, booking)
        return booking

    def get_status_history(
        self,
        user: UserContext,
        booking_id: str,
    ) -> list[ElderCareBookingStatusHistory]:
        self.get_booking(user, booking_id)

        return self.repository.get_status_history(
            booking_id
        )

    def _require_provider_access(
        self,
        user: UserContext,
        booking: ElderCareBooking,
    ) -> None:
        if (
            booking.provider_type
            == ElderCareProviderType.CAREGIVER
        ):
            if (
                user.role != Role.INDEPENDENT_CAREGIVER
                or booking.caregiver_user_id != user.user_id
            ):
                raise PermissionError(
                    "Only the assigned caregiver may review this booking"
                )

            if not self.repository.is_approved_elder_care_caregiver(
                user.user_id
            ):
                raise PermissionError(
                    "An approved elder-care caregiver is required"
                )

            return

        if (
            user.role != Role.CARE_HOME_STAFF
            or booking.organization_id is None
            or not self.repository.is_care_home_staff(
                user.user_id,
                booking.organization_id,
            )
        ):
            raise PermissionError(
                "Authorized staff of the care home must review this booking"
            )

    def decide_booking(
        self,
        user: UserContext,
        booking_id: str,
        request: ElderCareBookingDecisionRequest,
    ) -> ElderCareBooking:
        booking = self.get_booking(user, booking_id)
        self._require_provider_access(user, booking)

        return self.repository.transition_booking(
            booking_id=booking_id,
            actor_user_id=user.user_id,
            new_status=ElderCareBookingStatus(request.status),
            allowed_current_statuses=(
                ElderCareBookingStatus.REQUESTED,
            ),
            note=request.note,
        )

    def cancel_booking(
        self,
        user: UserContext,
        booking_id: str,
        request: ElderCareBookingNoteRequest,
    ) -> ElderCareBooking:
        booking = self.get_booking(user, booking_id)

        if (
            user.role not in REQUESTER_ROLES
            or booking.requester_user_id != user.user_id
        ):
            raise PermissionError(
                "Only the booking requester may cancel it"
            )

        return self.repository.transition_booking(
            booking_id=booking_id,
            actor_user_id=user.user_id,
            new_status=ElderCareBookingStatus.CANCELLED,
            allowed_current_statuses=(
                ElderCareBookingStatus.REQUESTED,
                ElderCareBookingStatus.APPROVED,
            ),
            note=request.note or "Booking cancelled by requester",
        )

    def complete_booking(
        self,
        user: UserContext,
        booking_id: str,
        request: ElderCareBookingNoteRequest,
    ) -> ElderCareBooking:
        booking = self.get_booking(user, booking_id)
        self._require_provider_access(user, booking)

        return self.repository.transition_booking(
            booking_id=booking_id,
            actor_user_id=user.user_id,
            new_status=ElderCareBookingStatus.COMPLETED,
            allowed_current_statuses=(
                ElderCareBookingStatus.APPROVED,
            ),
            note=request.note or "Service completed",
        )