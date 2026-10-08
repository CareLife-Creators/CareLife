import unittest
from datetime import date, datetime, timezone
from types import SimpleNamespace

from app.application.use_cases.children import ChildService
from app.domain.entities.child import (
    Child,
    OrphanageOutcome,
    OutcomeStatus,
    OutcomeType,
)
from app.domain.entities.user_context import Role, UserContext


class FakeChildRepository:
    def __init__(self):
        self.children = {}
        self.outcomes = {}

    def organization_is_orphanage(self, organization_id):
        return organization_id in {"orphanage-1", "orphanage-2"}

    def create(self, child):
        self.children[child.id] = child
        return child

    def list_by_orphanage(self, organization_id):
        return [
            child
            for child in self.children.values()
            if child.orphanage_organization_id == organization_id
        ]

    def get(self, child_id):
        return self.children.get(child_id)

    def update(self, child):
        self.children[child.id] = child
        return child

    def delete(self, child_id):
        return self.children.pop(child_id, None) is not None

    def create_outcome(self, outcome):
        self.outcomes[outcome.id] = outcome
        return outcome

    def list_outcomes(self, child_id):
        return [
            outcome
            for outcome in self.outcomes.values()
            if outcome.child_id == child_id
        ]

    def get_outcome(self, outcome_id):
        return self.outcomes.get(outcome_id)

    def update_outcome(self, outcome):
        self.outcomes[outcome.id] = outcome
        return outcome

    def delete_outcome(self, outcome_id):
        return self.outcomes.pop(outcome_id, None) is not None


def make_child(
    child_id="child-1",
    organization_id="orphanage-1",
):
    now = datetime.now(timezone.utc)
    return Child(
        id=child_id,
        parent_id=None,
        full_name="Ari Rahman",
        date_of_birth=date(2018, 5, 1),
        gender="female",
        allergies=None,
        medical_notes=None,
        orphanage_organization_id=organization_id,
        daycare_organization_id=None,
        created_at=now,
        updated_at=now,
    )


def make_staff(
    user_id="staff-1",
    organization_id="orphanage-1",
):
    return UserContext(
        user_id=user_id,
        role=Role.ORPHANAGE_STAFF,
        organization_id=organization_id,
    )


class ChildAccessControlTests(unittest.TestCase):
    def setUp(self):
        self.repository = FakeChildRepository()
        self.service = ChildService(self.repository)
        self.child = make_child()
        self.repository.children[self.child.id] = self.child

        self.outcome = OrphanageOutcome(
            id="outcome-1",
            child_id=self.child.id,
            organization_id="orphanage-1",
            outcome_type=OutcomeType.ADOPTION,
            outcome_status=OutcomeStatus.PENDING,
            outcome_date=date(2026, 10, 8),
            notes="Internal record",
            created_by="staff-1",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.repository.outcomes[self.outcome.id] = self.outcome

    def test_ac1_authorized_staff_can_read_child(self):
        child = self.service.get(make_staff(), self.child.id)
        self.assertEqual(child.id, self.child.id)

    def test_ac2_unauthorized_staff_cannot_read_child(self):
        other_staff = make_staff(
            user_id="staff-2",
            organization_id="orphanage-2",
        )

        with self.assertRaises(PermissionError):
            self.service.get(other_staff, self.child.id)

    def test_ac3_unauthorized_staff_cannot_update_child(self):
        other_staff = make_staff(
            user_id="staff-2",
            organization_id="orphanage-2",
        )

        with self.assertRaises(PermissionError):
            self.service.update(
                other_staff,
                self.child.id,
                SimpleNamespace(
                    full_name="Changed Name",
                    gender=None,
                    allergies=None,
                    medical_notes=None,
                ),
            )

    def test_ac4_child_access_is_isolated_by_organization(self):
        other_staff = make_staff(
            user_id="staff-2",
            organization_id="orphanage-2",
        )

        with self.assertRaises(PermissionError):
            self.service.get(other_staff, self.child.id)

        with self.assertRaises(PermissionError):
            self.service.get_outcome(other_staff, self.outcome.id)

    def test_ac5_public_role_cannot_access_private_child_or_outcome(self):
        public_user = UserContext(
            user_id="public-1",
            role=Role.PARENT_GUARDIAN,
        )

        with self.assertRaises(PermissionError):
            self.service.get(public_user, self.child.id)

        with self.assertRaises(PermissionError):
            self.service.get_outcome(public_user, self.outcome.id)

    def test_authorized_staff_can_read_outcome(self):
        outcome = self.service.get_outcome(
            make_staff(),
            self.outcome.id,
        )
        self.assertEqual(outcome.id, self.outcome.id)


if __name__ == "__main__":
    unittest.main()