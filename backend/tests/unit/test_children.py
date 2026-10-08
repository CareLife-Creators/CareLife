import unittest
from datetime import date, datetime, timezone
from types import SimpleNamespace

from app.application.use_cases.children import ChildService
from app.domain.entities.child import (
    Child,
    ChildContact,
    ContactType,
    OrphanageOutcome,
    OutcomeStatus,
    OutcomeType,
)
from app.domain.entities.user_context import Role, UserContext


class FakeChildRepository:
    def __init__(self):
        self.children = {}
        self.outcomes = {}
        self.contacts = {}

    def organization_is_orphanage(self, organization_id):
        return organization_id in {
            "orphanage-1",
            "orphanage-2",
        }

    def create(self, child):
        self.children[child.id] = child
        return child

    def list_by_orphanage(self, organization_id):
        return [
            child
            for child in self.children.values()
            if child.orphanage_organization_id == organization_id
        ]

    def list_by_parent(self, parent_id):
        return [
            child
            for child in self.children.values()
            if child.parent_id == parent_id
        ]

    def get(self, child_id):
        return self.children.get(child_id)

    def update(self, child):
        self.children[child.id] = child
        return child

    def delete(self, child_id):
        return self.children.pop(
            child_id,
            None,
        ) is not None

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
        return self.outcomes.pop(
            outcome_id,
            None,
        ) is not None

    def create_contact(self, contact):
        self.contacts[contact.id] = contact
        return contact

    def get_contact(self, contact_id):
        return self.contacts.get(contact_id)

    def list_contacts(self, child_id, contact_type):
        return [
            contact
            for contact in self.contacts.values()
            if contact.child_id == child_id
            and contact.contact_type.value == contact_type
        ]


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


def make_parent(
    user_id="parent-1",
):
    return UserContext(
        user_id=user_id,
        role=Role.PARENT_GUARDIAN,
    )


def make_daycare_staff(
    user_id="staff-1",
    organization_id="daycare-1",
):
    return UserContext(
        user_id=user_id,
        role=Role.DAYCARE_STAFF,
        organization_id=organization_id,
    )


def make_orphanage_staff(
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

        self.repository.children[
            self.child.id
        ] = self.child

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

        self.repository.outcomes[
            self.outcome.id
        ] = self.outcome

    def test_ac1_authorized_staff_can_read_child(self):
        child = self.service.get(
            make_orphanage_staff(),
            self.child.id,
        )

        self.assertEqual(
            child.id,
            self.child.id,
        )

    def test_ac2_unauthorized_staff_cannot_read_child(self):
        other_staff = make_orphanage_staff(
            user_id="staff-2",
            organization_id="orphanage-2",
        )

        with self.assertRaises(PermissionError):
            self.service.get(
                other_staff,
                self.child.id,
            )

    def test_ac3_unauthorized_staff_cannot_update_child(self):
        other_staff = make_orphanage_staff(
            user_id="staff-2",
            organization_id="orphanage-2",
        )

        with self.assertRaises(PermissionError):
            self.service.update(
                other_staff,
                self.child.id,
                SimpleNamespace(
                    full_name="Changed Name",
                    date_of_birth=None,
                    gender=None,
                    allergies=None,
                    medical_notes=None,
                ),
            )

    def test_ac4_child_access_is_isolated_by_organization(self):
        other_staff = make_orphanage_staff(
            user_id="staff-2",
            organization_id="orphanage-2",
        )

        with self.assertRaises(PermissionError):
            self.service.get(
                other_staff,
                self.child.id,
            )

        with self.assertRaises(PermissionError):
            self.service.get_outcome(
                other_staff,
                self.outcome.id,
            )

    def test_ac5_public_role_cannot_access_private_child_or_outcome(self):
        public_user = UserContext(
            user_id="public-1",
            role=Role.PARENT_GUARDIAN,
        )

        with self.assertRaises(PermissionError):
            self.service.get(
                public_user,
                self.child.id,
            )

        with self.assertRaises(PermissionError):
            self.service.get_outcome(
                public_user,
                self.outcome.id,
            )

    def test_authorized_staff_can_read_outcome(self):
        outcome = self.service.get_outcome(
            make_orphanage_staff(),
            self.outcome.id,
        )

        self.assertEqual(
            outcome.id,
            self.outcome.id,
        )


class DaycareChildProfileTests(unittest.TestCase):
    def setUp(self):
        self.repository = FakeChildRepository()
        self.service = ChildService(self.repository)

    def test_ac1_parent_can_create_child_profile(self):
        parent = make_parent()

        request = SimpleNamespace(
            full_name="Mina Rahman",
            date_of_birth=date(2019, 7, 15),
            gender="female",
            allergies="Peanuts",
            medical_notes="Asthma",
        )

        child = self.service.create_daycare_child(
            parent,
            request,
        )

        self.assertEqual(
            child.parent_id,
            parent.user_id,
        )
        self.assertEqual(
            child.full_name,
            "Mina Rahman",
        )

    def test_ac2_parent_can_update_owned_child_profile(self):
        parent = make_parent()

        child = Child(
            id="daycare-child-1",
            parent_id=parent.user_id,
            full_name="Old Name",
            date_of_birth=date(2019, 1, 1),
            gender="male",
            allergies=None,
            medical_notes=None,
            orphanage_organization_id=None,
            daycare_organization_id=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.repository.children[
            child.id
        ] = child

        request = SimpleNamespace(
            full_name="New Name",
            date_of_birth=None,
            gender=None,
            allergies=None,
            medical_notes="Updated notes",
        )

        updated = self.service.update_daycare_child(
            parent,
            child.id,
            request,
        )

        self.assertEqual(
            updated.full_name,
            "New Name",
        )
        self.assertEqual(
            updated.medical_notes,
            "Updated notes",
        )

    def test_ac3_parent_can_add_emergency_contact(self):
        parent = make_parent()

        child = Child(
            id="daycare-child-2",
            parent_id=parent.user_id,
            full_name="Mina Rahman",
            date_of_birth=date(2019, 1, 1),
            gender="female",
            allergies=None,
            medical_notes=None,
            orphanage_organization_id=None,
            daycare_organization_id=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.repository.children[
            child.id
        ] = child

        request = SimpleNamespace(
            full_name="Rahim Rahman",
            relationship_to_child="Father",
            phone="01710000000",
            email="rahim@example.com",
            address="Dhaka",
        )

        contact = self.service.add_emergency_contact(
            parent,
            child.id,
            request,
        )

        self.assertEqual(
            contact.child_id,
            child.id,
        )
        self.assertEqual(
            contact.contact_type,
            ContactType.EMERGENCY,
        )

    def test_ac4_parent_can_add_pickup_person(self):
        parent = make_parent()

        child = Child(
            id="daycare-child-3",
            parent_id=parent.user_id,
            full_name="Mina Rahman",
            date_of_birth=date(2019, 1, 1),
            gender="female",
            allergies=None,
            medical_notes=None,
            orphanage_organization_id=None,
            daycare_organization_id="daycare-1",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.repository.children[
            child.id
        ] = child

        request = SimpleNamespace(
            full_name="Sara Rahman",
            relationship_to_child="Aunt",
            phone="01810000000",
            email="sara@example.com",
            address="Dhaka",
        )

        contact = self.service.add_pickup_person(
            parent,
            child.id,
            request,
        )

        self.assertEqual(
            contact.contact_type,
            ContactType.PICKUP,
        )

    def test_ac5_authorized_daycare_staff_can_read_pickup_info(self):
        parent = make_parent()

        child = Child(
            id="daycare-child-4",
            parent_id=parent.user_id,
            full_name="Mina Rahman",
            date_of_birth=date(2019, 1, 1),
            gender="female",
            allergies=None,
            medical_notes=None,
            orphanage_organization_id=None,
            daycare_organization_id="daycare-1",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.repository.children[
            child.id
        ] = child

        pickup = ChildContact(
            id="pickup-1",
            child_id=child.id,
            contact_type=ContactType.PICKUP,
            full_name="Sara Rahman",
            relationship_to_child="Aunt",
            phone="01810000000",
            email=None,
            address=None,
            created_by=parent.user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.repository.contacts[
            pickup.id
        ] = pickup

        staff = make_daycare_staff(
            organization_id="daycare-1",
        )

        contacts = self.service.list_pickup_persons(
            staff,
            child.id,
        )

        self.assertEqual(
            len(contacts),
            1,
        )
        self.assertEqual(
            contacts[0].full_name,
            "Sara Rahman",
        )

    def test_ac6_unrelated_user_cannot_access_child(self):
        owner = make_parent("parent-1")
        other_parent = make_parent("parent-2")

        child = Child(
            id="daycare-child-5",
            parent_id=owner.user_id,
            full_name="Mina Rahman",
            date_of_birth=date(2019, 1, 1),
            gender="female",
            allergies=None,
            medical_notes=None,
            orphanage_organization_id=None,
            daycare_organization_id="daycare-1",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.repository.children[
            child.id
        ] = child

        with self.assertRaises(PermissionError):
            self.service.get_daycare_child(
                other_parent,
                child.id,
            )

    def test_ac6_wrong_daycare_staff_cannot_access_pickup(self):
        owner = make_parent()

        child = Child(
            id="daycare-child-6",
            parent_id=owner.user_id,
            full_name="Mina Rahman",
            date_of_birth=date(2019, 1, 1),
            gender="female",
            allergies=None,
            medical_notes=None,
            orphanage_organization_id=None,
            daycare_organization_id="daycare-1",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        self.repository.children[
            child.id
        ] = child

        wrong_staff = make_daycare_staff(
            organization_id="daycare-2",
        )

        with self.assertRaises(PermissionError):
            self.service.list_pickup_persons(
                wrong_staff,
                child.id,
            )


if __name__ == "__main__":
    unittest.main()