import unittest
from datetime import datetime, timezone
from unittest.mock import Mock

from app.application.use_cases.audit_log import AuditLogService
from app.domain.entities.audit_log import AuditLog
from app.infrastructure.repositories.audit_log_repository import (
    PostgresAuditLogRepository,
)


def make_audit_log() -> AuditLog:
    return AuditLog(
        id="audit-1",
        actor_user_id="admin-1",
        actor_role="carelife_admin",
        action="organization.verification.approved",
        target_type="organization",
        target_id="org-1",
        created_at=datetime.now(timezone.utc),
    )


class AuditLogServiceTests(unittest.TestCase):

    def test_list_logs_delegates_pagination_to_repository(self):
        repository = Mock()
        expected_logs = [make_audit_log()]
        repository.list_logs.return_value = expected_logs

        service = AuditLogService(repository)

        result = service.list_logs(
            limit=10,
            offset=20,
        )

        self.assertEqual(result, expected_logs)
        repository.list_logs.assert_called_once_with(
            limit=10,
            offset=20,
        )

    def test_record_uses_the_callers_transaction(self):
        connection = Mock()
        repository = PostgresAuditLogRepository()

        repository.record_on_connection(
            connection,
            actor_user_id="admin-1",
            actor_role="carelife_admin",
            action="organization.verification.approved",
            target_type="organization",
            target_id="org-1",
        )

        connection.execute.assert_called_once()
        query, parameters = connection.execute.call_args.args

        self.assertIn("INSERT INTO audit_logs", query)
        self.assertEqual(
            parameters[1:],
            (
                "admin-1",
                "carelife_admin",
                "organization.verification.approved",
                "organization",
                "org-1",
            ),
        )


if __name__ == "__main__":
    unittest.main()
