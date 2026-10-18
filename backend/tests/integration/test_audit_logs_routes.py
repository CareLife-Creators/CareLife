import unittest
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.application.use_cases.audit_log import AuditLogService
from app.domain.entities.audit_log import AuditLog
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.audit_log import (
    get_audit_log_service,
)
from app.presentation.api.dependencies.authorization import (
    get_current_user,
)
from main import app


class FakeAuditLogRepository:

    def __init__(self):
        now = datetime.now(timezone.utc)
        self.logs = [
            AuditLog(
                id="audit-1",
                actor_user_id="admin-1",
                actor_role="carelife_admin",
                action="organization.verification.approved",
                target_type="organization",
                target_id="org-1",
                created_at=now,
            ),
            AuditLog(
                id="audit-2",
                actor_user_id="admin-2",
                actor_role="carelife_admin",
                action="organization.verification.rejected",
                target_type="organization",
                target_id="org-2",
                created_at=now,
            ),
        ]

    def list_logs(
        self,
        limit: int,
        offset: int,
    ) -> list[AuditLog]:
        return self.logs[offset:offset + limit]


class AuditLogRouteTests(unittest.TestCase):

    def setUp(self):
        self.repository = FakeAuditLogRepository()
        self.service = AuditLogService(self.repository)
        self.current_user = UserContext(
            user_id="admin-1",
            role=Role.CARELIFE_ADMIN,
        )

        app.dependency_overrides[
            get_audit_log_service
        ] = lambda: self.service
        app.dependency_overrides[
            get_current_user
        ] = lambda: self.current_user

        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_admin_can_read_audit_logs(self):
        response = self.client.get("/admin/audit-logs")

        self.assertEqual(response.status_code, 200)
        body = response.json()

        self.assertEqual(len(body), 2)
        self.assertEqual(body[0]["actor_user_id"], "admin-1")
        self.assertEqual(body[0]["actor_role"], "carelife_admin")
        self.assertEqual(
            body[0]["action"],
            "organization.verification.approved",
        )
        self.assertEqual(body[0]["target_type"], "organization")
        self.assertEqual(body[0]["target_id"], "org-1")
        self.assertIn("created_at", body[0])

    def test_pagination_returns_requested_page(self):
        response = self.client.get(
            "/admin/audit-logs?limit=1&offset=1"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], "audit-2")

    def test_non_admin_cannot_read_audit_logs(self):
        self.current_user = UserContext(
            user_id="parent-1",
            role=Role.PARENT_GUARDIAN,
        )

        response = self.client.get("/admin/audit-logs")

        self.assertEqual(response.status_code, 403)

    def test_audit_log_endpoint_is_read_only(self):
        for method in ("post", "put", "patch", "delete"):
            with self.subTest(method=method):
                response = getattr(self.client, method)(
                    "/admin/audit-logs"
                )
                self.assertIn(response.status_code, (404, 405))

    def test_page_size_above_limit_is_rejected(self):
        response = self.client.get(
            "/admin/audit-logs?limit=101"
        )

        self.assertEqual(response.status_code, 422)

    def test_negative_offset_is_rejected(self):
        response = self.client.get(
            "/admin/audit-logs?offset=-1"
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
