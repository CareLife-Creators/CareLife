import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.application.use_cases.elder_care_booking import (
    ElderCareBookingService,
)
from app.domain.entities.elder_care_booking import (
    ElderCareBooking,
    ElderCareBookingStatus,
    ElderCareBookingStatusHistory,
    ElderCareProviderType,
)
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import (
    get_current_user,
)
from app.presentation.api.dependencies.elder_care_booking import (
    get_elder_care_booking_service,
)
from main import app


class ElderCareBookingRouteTests(unittest.TestCase):

    def setUp(self):
        self.service = Mock(spec=ElderCareBookingService)

        self.current_user = UserContext(
            user_id="family-1",
            role=Role.FAMILY_REPRESENTATIVE,
        )

        app.dependency_overrides[get_current_user] = (
            lambda: self.current_user
        )

        app.dependency_overrides[
            get_elder_care_booking_service
        ] = lambda: self.service

        self.client = TestClient(app)

        starts_at = datetime.now(timezone.utc) + timedelta(days=2)
        ends_at = starts_at + timedelta(hours=1)

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
            message=None,
            created_at=starts_at,
            updated_at=starts_at,
        )

    def tearDown(self):
        app.dependency_overrides.pop(
            get_current_user,
            None,
        )
        app.dependency_overrides.pop(
            get_elder_care_booking_service,
            None,
        )

    def test_create_booking_returns_201(self):
        self.service.create_booking.return_value = self.booking

        response = self.client.post(
            "/elder-care/bookings",
            json={
                "resident_id": "resident-1",
                "provider_type": "caregiver",
                "provider_id": "caregiver-1",
                "service_type": "Personal care",
                "starts_at": self.booking.starts_at.isoformat(),
                "ends_at": self.booking.ends_at.isoformat(),
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["id"], "booking-1")
        self.assertEqual(
            response.json()["status"],
            "requested",
        )
        self.assertEqual(
            response.json()["provider_id"],
            "caregiver-1",
        )

        self.service.create_booking.assert_called_once()

    def test_unrelated_role_cannot_create_booking(self):
        self.current_user = UserContext(
            user_id="admin-1",
            role=Role.CARELIFE_ADMIN,
        )

        response = self.client.post(
            "/elder-care/bookings",
            json={
                "resident_id": "resident-1",
                "provider_type": "caregiver",
                "provider_id": "caregiver-1",
                "service_type": "Personal care",
                "starts_at": self.booking.starts_at.isoformat(),
                "ends_at": self.booking.ends_at.isoformat(),
            },
        )

        self.assertEqual(response.status_code, 403)
        self.service.create_booking.assert_not_called()

    def test_status_history_is_returned_in_sequence_order(self):
        self.service.get_status_history.return_value = [
            ElderCareBookingStatusHistory(
                id="history-1",
                booking_id="booking-1",
                sequence_no=1,
                from_status=None,
                to_status=ElderCareBookingStatus.REQUESTED,
                changed_by="family-1",
                note="Booking requested",
                created_at=self.booking.created_at,
            )
        ]

        response = self.client.get(
            "/elder-care/bookings/booking-1/history"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["sequence_no"], 1)
        self.assertEqual(
            response.json()[0]["to_status"],
            "requested",
        )


if __name__ == "__main__":
    unittest.main()