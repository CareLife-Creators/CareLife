from uuid import uuid4

import psycopg

from app.domain.entities.audit_log import AuditLog
from app.infrastructure.database.connection import get_connection


class PostgresAuditLogRepository:

    def record_on_connection(
        self,
        connection: psycopg.Connection,
        *,
        actor_user_id: str,
        actor_role: str,
        action: str,
        target_type: str,
        target_id: str,
    ) -> None:
        """
        Insert an audit event using the caller's transaction.

        Do not commit here. The business operation and its audit
        event must be committed or rolled back together.
        """
        connection.execute(
            """
            INSERT INTO audit_logs (
                id,
                actor_user_id,
                actor_role,
                action,
                target_type,
                target_id
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                str(uuid4()),
                actor_user_id,
                actor_role,
                action,
                target_type,
                target_id,
            ),
        )

    def list_logs(
        self,
        limit: int,
        offset: int,
    ) -> list[AuditLog]:
        if not 1 <= limit <= 100:
            raise ValueError(
                "Limit must be between 1 and 100."
            )

        if offset < 0:
            raise ValueError(
                "Offset cannot be negative."
            )

        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    actor_user_id,
                    actor_role,
                    action,
                    target_type,
                    target_id,
                    created_at
                FROM audit_logs
                ORDER BY created_at DESC, id DESC
                LIMIT %s OFFSET %s
                """,
                (limit, offset),
            ).fetchall()

        return [
            AuditLog(
                id=row[0],
                actor_user_id=row[1],
                actor_role=row[2],
                action=row[3],
                target_type=row[4],
                target_id=row[5],
                created_at=row[6],
            )
            for row in rows
        ]