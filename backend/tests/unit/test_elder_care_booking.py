import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from app.application.interfaces.elder_care_booking import (
    ElderCareBookingRepository,
)
from app.application.schemas.elder_care_booking import (
    ElderCareBookingCreateRequest,
    ElderCareBookingNoteRequest,
)
from app.application.use_cases.elder_care_booking import (
    ElderCareBookingService,
)
from app.domain.entities.elder_care_booking import (
    ElderCareBooking,
    ElderCareBookingStatus,
    ElderCareProviderType,
)
from app.domain.entities.user_context import Role, UserContext


class ElderCareBookingServiceTests(unittest.TestCase):

    def setUp(self):
        self.repository = Mock(
            spec=ElderCareBookingRepository
        )

        self.service = ElderCareBookingService(
            repository=self.repository
        )

        self.user = UserContext(
            user_id="family-1",
            role=Role.FAMILY_REPRESENTATIVE,
        )

        starts_at = datetime.now(timezone.utc) + timedelta(days=2)
        ends_at = starts_at + timedelta(hours=1)

        self.request = ElderCareBookingCreateRequest(
            resident_id="resident-1",
            provider_type="caregiver",
            provider_id="caregiver-1",
            service_type="Personal care",
            starts_at=starts_at,
            ends_at=ends_at,
            message="Please confirm the appointment.",
        )

        self.booking = ElderCareBooking(
            id="booking-1",
            resident_id="resident-1",
            resident_organization_id="home-1",
            requester_user_id="family-1",
            provider_type=ElderCareProviderType.CAREGIVER,
            caregiver_user_id="caregiver-1",
            organization_id=None,
            availability_id="slot-1",
            service_type="Personal care",
            starts_at=starts_at,
            ends_at=ends_at,
            status=ElderCareBookingStatus.REQUESTED,
            message="Please confirm the appointment.",
            created_at=starts_at,
            updated_at=starts_at,
        )

    def test_authorized_family_can_create_booking(self):
        self.repository.create_booking.return_value = self.booking

        result = self.service.create_booking(
            self.user,
            self.request,
        )

        self.assertEqual(result.id, "booking-1")

        self.repository.create_booking.assert_called_once_with(
            requester_user_id="family-1",
            values=self.request.model_dump(),
        )

    def test_unrelated_role_cannot_create_booking(self):
        admin = UserContext(
            user_id="admin-1",
            role=Role.CARELIFE_ADMIN,
        )

        with self.assertRaises(PermissionError):
            self.service.create_booking(
                admin,
                self.request,
            )

        self.repository.create_booking.assert_not_called()

    def test_past_booking_is_rejected(self):
        past_start = (
            datetime.now(timezone.utc) - timedelta(days=1)
        )

        request = ElderCareBookingCreateRequest(
            resident_id="resident-1",
            provider_type="caregiver",
            provider_id="caregiver-1",
            service_type="Personal care",
            starts_at=past_start,
            ends_at=past_start + timedelta(hours=1),
        )

        with self.assertRaisesRegex(
            ValueError,
            "must start in the future",
        ):
            self.service.create_booking(
                self.user,
                request,
            )

        self.repository.create_booking.assert_not_called()

    def test_requester_can_cancel_booking(self):
        self.repository.get_booking.return_value = self.booking
        self.repository.transition_booking.return_value = (
            self.booking.model_copy(
                update={
                    "status": ElderCareBookingStatus.CANCELLED,
                    "cancelled_by": "family-1",
                }
            )
        )

        result = self.service.cancel_booking(
            self.user,
            "booking-1",
            ElderCareBookingNoteRequest(
                note="Schedule changed"
            ),
        )

        self.assertEqual(
            result.status,
            ElderCareBookingStatus.CANCELLED,
        )

        self.repository.transition_booking.assert_called_once_with(
            booking_id="booking-1",
            actor_user_id="family-1",
            new_status=ElderCareBookingStatus.CANCELLED,
            allowed_current_statuses=(
                ElderCareBookingStatus.REQUESTED,
                ElderCareBookingStatus.APPROVED,
            ),
            note="Schedule changed",
        )

    def test_another_family_cannot_cancel_booking(self):
        self.repository.get_booking.return_value = self.booking

        another_family = UserContext(
            user_id="family-2",
            role=Role.FAMILY_REPRESENTATIVE,
        )

        with self.assertRaises(PermissionError):
            self.service.cancel_booking(
                another_family,
                "booking-1",
                ElderCareBookingNoteRequest(),
            )

        self.repository.transition_booking.assert_not_called()

    def test_caregiver_cannot_cancel_requester_booking(self):
        self.repository.get_booking.return_value = self.booking

        caregiver = UserContext(
            user_id="caregiver-1",
            role=Role.INDEPENDENT_CAREGIVER,
        )

        with self.assertRaises(PermissionError):
            self.service.cancel_booking(
                caregiver,
                "booking-1",
                ElderCareBookingNoteRequest(),
            )

        self.repository.transition_booking.assert_not_called()


if __name__ == "__main__":
    unittest.main()