import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from app.infrastructure.repositories.caregiver_booking import (
    PostgresCaregiverBookingRepository,
)


class CaregiverBookingRepositoryTests(unittest.TestCase):

    @patch(
        "app.infrastructure.repositories.caregiver_booking.get_connection"
    )
    def test_rejects_slot_that_has_started_even_if_it_has_not_ended(
        self,
        get_connection_mock,
    ):
        now = datetime.now(timezone.utc)
        slot_row = (
            "slot-1",
            "caregiver-1",
            now - timedelta(minutes=5),
            now + timedelta(minutes=30),
            "nanny",
        )

        connection = MagicMock()
        connection_context = MagicMock()
        connection_context.__enter__.return_value = connection
        get_connection_mock.return_value = connection_context

        slot_result = MagicMock()
        slot_result.fetchone.return_value = slot_row
        active_booking_result = MagicMock()
        active_booking_result.fetchone.return_value = None
        insert_result = MagicMock()
        insert_result.fetchone.return_value = (
            "appointment-1",
            "slot-1",
            "caregiver-1",
            "parent-1",
            "nanny",
            slot_row[2],
            slot_row[3],
            "requested",
            None,
            None,
            None,
            None,
            now,
            now,
        )
        connection.execute.side_effect = [
            slot_result,
            active_booking_result,
            insert_result,
        ]

        repository = PostgresCaregiverBookingRepository()

        with self.assertRaisesRegex(
            ValueError,
            "already started or expired",
        ):
            repository.create_appointment(
                requester_user_id="parent-1",
                availability_id="slot-1",
                message=None,
            )

        connection.execute.assert_called_once()


if __name__ == "__main__":
    unittest.main()
