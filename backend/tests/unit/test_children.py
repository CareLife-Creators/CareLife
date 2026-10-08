import unittest
from datetime import date, datetime, timezone
from types import SimpleNamespace

from app.application.use_cases.children import ChildService
from app.domain.entities.child import Child
from app.domain.entities.user_context import Role, UserContext


class FakeChildRepository:
    def __init__(self):
        self.children = {}

    def organization_is_orphanage(self, organization_id):
        return organization_id == "orphanage-1"

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
        return outcome

    def list_outcomes(self, child_id):
        return []

    def get_outcome(self, outcome_id):
        return None

    def update_outcome(self, outcome):
        return outcome

    def delete_outcome(self, outcome_id):
        return False


class ChildServiceTests(unittest.TestCase):
    def test_staff_can_create_child_for_own_orphanage(self):
        repository = FakeChildRepository()
        service = ChildService(repository)
        user = UserContext(
            user_id="staff-1",
            role=Role.ORPHANAGE_STAFF,
            organization_id="orphanage-1",
        )

        child = service.create(
            user,
            "orphanage-1",
            SimpleNamespace(
                full_name="Ari Rahman",
                date_of_birth=date(2018, 5, 1),
                gender="female",
                allergies=None,
                medical_notes=None,
            ),
        )

        self.assertEqual(child.full_name, "Ari Rahman")
        self.assertEqual(child.orphanage_organization_id, "orphanage-1")

    def test_staff_cannot_read_child_from_another_orphanage(self):
        repository = FakeChildRepository()
        child = Child(
            id="child-1",
            parent_id=None,
            full_name="Ari Rahman",
            date_of_birth=date(2018, 5, 1),
            gender="female",
            allergies=None,
            medical_notes=None,
            orphanage_organization_id="orphanage-2",
            daycare_organization_id=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        repository.children[child.id] = child
        service = ChildService(repository)
        user = UserContext(
            user_id="staff-1",
            role=Role.ORPHANAGE_STAFF,
            organization_id="orphanage-1",
        )

        with self.assertRaises(PermissionError):
            service.get(user, "child-1")


if __name__ == "__main__":
    unittest.main()
