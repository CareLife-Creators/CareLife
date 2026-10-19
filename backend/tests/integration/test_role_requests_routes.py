import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.application.use_cases.role_requests import RoleRequestService
from app.domain.entities.role_request import RoleRequest
from app.domain.entities.user import User
from app.presentation.api.dependencies.authentication import get_bearer_token
from app.presentation.api.dependencies.role_requests import get_role_request_service
from main import app


class FakeRoleRequestRepository:
    def __init__(self):
        self.requests = {}
        self.user_roles = {}
        self.audit_events = []
        self.counter = 0

    def create(self, user_id, requested_role, note):
        if any(
            item.user_id == user_id and item.status == "pending"
            for item in self.requests.values()
        ):
            raise ValueError("A pending staff role request already exists.")
        self.counter += 1
        request = RoleRequest(
            id=f"role-request-{self.counter}",
            user_id=user_id,
            requested_role=requested_role,
            note=note,
            status="pending",
            created_at=datetime.now(timezone.utc),
        )
        self.requests[request.id] = request
        return request

    def list_for_user(self, user_id):
        return [
            item for item in self.requests.values()
            if item.user_id == user_id
        ]

    def list_by_status(self, status):
        return [
            item for item in self.requests.values()
            if item.status == status
        ]

    def approve(self, request_id, reviewer_id, reviewer_role):
        request = self.requests.get(request_id)
        if request is None:
            return None
        if request.status != "pending":
            raise ValueError("This role request has already been reviewed.")
        approved = request.model_copy(update={
            "status": "approved",
            "reviewed_at": datetime.now(timezone.utc),
            "reviewed_by": reviewer_id,
        })
        self.requests[request_id] = approved
        self.user_roles[request.user_id] = request.requested_role
        self.audit_events.append({
            "actor_user_id": reviewer_id,
            "actor_role": reviewer_role,
            "action": "user.role_request.approved",
            "target_type": "role_request",
            "target_id": request_id,
        })
        return approved

    def reject(self, request_id, reviewer_id, reviewer_role):
        request = self.requests.get(request_id)
        if request is None:
            return None
        if request.status != "pending":
            raise ValueError("This role request has already been reviewed.")
        rejected = request.model_copy(update={
            "status": "rejected",
            "reviewed_at": datetime.now(timezone.utc),
            "reviewed_by": reviewer_id,
        })
        self.requests[request_id] = rejected
        self.audit_events.append({
            "actor_user_id": reviewer_id,
            "actor_role": reviewer_role,
            "action": "user.role_request.rejected",
            "target_type": "role_request",
            "target_id": request_id,
        })
        return rejected


class RoleRequestRoutesTests(unittest.TestCase):
    def setUp(self):
        self.repository = FakeRoleRequestRepository()
        self.service = RoleRequestService(self.repository)
        self.db_user = User(
            id="parent-1",
            email="parent@example.com",
            password_hash="test-hash",
            role_name="parent_guardian",
        )
        app.dependency_overrides[get_role_request_service] = (
            lambda: self.service
        )
        # Keep get_authenticated_user and require_role real. Mock only
        # token decoding/session persistence/user lookup so every request
        # reloads the role from the repository boundary.
        app.dependency_overrides[get_bearer_token] = lambda: "valid-token"
        self.decode_patcher = patch(
            "app.presentation.api.dependencies.authentication.decode_access_token",
            side_effect=lambda _token: {
                "jti": "test-token-id",
                "sub": self.db_user.id,
            },
        )
        self.revoked_patcher = patch(
            "app.presentation.api.dependencies.authentication.PostgresSessionRepository.is_token_revoked",
            return_value=False,
        )
        self.user_lookup_patcher = patch(
            "app.presentation.api.dependencies.authentication.PostgresUserRepository.get_by_id",
            side_effect=lambda user_id: (
                self.db_user if self.db_user.id == user_id else None
            ),
        )
        self.decode_patcher.start()
        self.revoked_patcher.start()
        self.user_lookup_patcher.start()
        self.client = TestClient(app)

    def tearDown(self):
        self.user_lookup_patcher.stop()
        self.revoked_patcher.stop()
        self.decode_patcher.stop()
        app.dependency_overrides.clear()

    def request_staff_role(self, role="daycare_staff"):
        return self.client.post(
            "/users/me/role-requests",
            json={"requested_role": role, "note": "Staff application"},
        )

    def become_admin(self):
        self.db_user = User(
            id="admin-1",
            email="admin@example.com",
            password_hash="test-hash",
            role_name="carelife_admin",
        )

    def test_user_can_create_and_list_own_role_requests(self):
        created = self.request_staff_role()
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()["status"], "pending")
        self.assertEqual(created.json()["user_id"], "parent-1")
        self.assertEqual(created.json()["requested_role"], "daycare_staff")

        listed = self.client.get("/users/me/role-requests")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.json()), 1)
        self.assertEqual(listed.json()[0]["id"], created.json()["id"])

    def test_only_one_pending_request_per_user(self):
        first = self.request_staff_role("daycare_staff")
        second = self.request_staff_role("care_home_staff")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 409)
        self.assertEqual(
            second.json(),
            {"detail": "A pending staff role request already exists."},
        )

    def test_invalid_role_request_is_rejected(self):
        for role in (
            "parent_guardian",
            "donor_supporter",
            "carelife_admin",
            "unknown",
        ):
            with self.subTest(role=role):
                response = self.request_staff_role(role)
                self.assertEqual(response.status_code, 422)

    def test_admin_can_list_pending_requests(self):
        created = self.request_staff_role()
        self.assertEqual(created.status_code, 201)
        self.become_admin()

        response = self.client.get("/admin/role-requests?status=pending")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], created.json()["id"])

    def test_admin_can_approve_and_audit_is_written(self):
        created = self.request_staff_role("orphanage_staff")
        request_id = created.json()["id"]
        self.become_admin()

        response = self.client.post(
            f"/admin/role-requests/{request_id}/approve"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "approved")
        self.assertEqual(response.json()["reviewed_by"], "admin-1")
        self.assertEqual(
            self.repository.user_roles["parent-1"],
            "orphanage_staff",
        )
        self.assertEqual(
            self.repository.audit_events[-1]["action"],
            "user.role_request.approved",
        )
        self.assertEqual(
            self.repository.audit_events[-1]["actor_role"],
            "carelife_admin",
        )

    def test_admin_can_reject_and_audit_is_written(self):
        created = self.request_staff_role("care_home_staff")
        request_id = created.json()["id"]
        self.become_admin()

        response = self.client.post(
            f"/admin/role-requests/{request_id}/reject"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "rejected")
        self.assertNotIn("parent-1", self.repository.user_roles)
        self.assertEqual(
            self.repository.audit_events[-1]["action"],
            "user.role_request.rejected",
        )

    def test_non_admin_is_blocked_from_admin_role_request_routes(self):
        created = self.request_staff_role()
        request_id = created.json()["id"]

        list_response = self.client.get("/admin/role-requests")
        approve_response = self.client.post(
            f"/admin/role-requests/{request_id}/approve"
        )
        reject_response = self.client.post(
            f"/admin/role-requests/{request_id}/reject"
        )

        self.assertEqual(list_response.status_code, 403)
        self.assertEqual(approve_response.status_code, 403)
        self.assertEqual(reject_response.status_code, 403)
        self.assertEqual(
            self.repository.requests[request_id].status,
            "pending",
        )
        self.assertEqual(self.repository.audit_events, [])

    def test_role_is_reloaded_from_database_on_each_request(self):
        first = self.client.get("/admin/role-requests")
        self.assertEqual(first.status_code, 403)

        # Simulate the persisted role change made by an approved request.
        # The next request must observe the newly-read role immediately.
        self.db_user = self.db_user.model_copy(
            update={"role_name": "carelife_admin"}
        )
        second = self.client.get("/admin/role-requests")
        self.assertEqual(second.status_code, 200)


if __name__ == "__main__":
    unittest.main()
