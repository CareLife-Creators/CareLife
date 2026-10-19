from uuid import uuid4

import psycopg
from psycopg.errors import UniqueViolation

from app.domain.entities.role_request import RoleRequest
from app.infrastructure.database.connection import get_connection
from app.infrastructure.repositories.audit_log_repository import (
    PostgresAuditLogRepository,
)


_SELECT_COLUMNS = """
    id,
    user_id,
    requested_role,
    note,
    status,
    created_at,
    reviewed_at,
    reviewed_by
"""


def _to_entity(row) -> RoleRequest:
    return RoleRequest(
        id=row[0],
        user_id=row[1],
        requested_role=row[2],
        note=row[3],
        status=row[4],
        created_at=row[5],
        reviewed_at=row[6],
        reviewed_by=row[7],
    )


class PostgresRoleRequestRepository:
    def __init__(self):
        self.audit_logs = PostgresAuditLogRepository()

    def create(
        self,
        user_id: str,
        requested_role: str,
        note: str | None,
    ) -> RoleRequest:
        try:
            with get_connection() as connection:
                with connection.transaction():
                    row = connection.execute(
                        """
                        INSERT INTO user_role_requests (
                            id,
                            user_id,
                            requested_role,
                            note,
                            status
                        )
                        VALUES (%s, %s, %s, %s, 'pending')
                        RETURNING
                            id,
                            user_id,
                            requested_role,
                            note,
                            status,
                            created_at,
                            reviewed_at,
                            reviewed_by
                        """,
                        (
                            str(uuid4()),
                            user_id,
                            requested_role,
                            note,
                        ),
                    ).fetchone()
            return _to_entity(row)
        except UniqueViolation as exc:
            raise ValueError(
                "A pending staff role request already exists."
            ) from exc

    def list_for_user(self, user_id: str) -> list[RoleRequest]:
        with get_connection() as connection:
            rows = connection.execute(
                f"""
                SELECT {_SELECT_COLUMNS}
                FROM user_role_requests
                WHERE user_id = %s
                ORDER BY created_at DESC, id DESC
                """,
                (user_id,),
            ).fetchall()
        return [_to_entity(row) for row in rows]

    def list_by_status(self, status: str) -> list[RoleRequest]:
        with get_connection() as connection:
            rows = connection.execute(
                f"""
                SELECT {_SELECT_COLUMNS}
                FROM user_role_requests
                WHERE status = %s
                ORDER BY created_at ASC, id ASC
                """,
                (status,),
            ).fetchall()
        return [_to_entity(row) for row in rows]

    def approve(
        self,
        request_id: str,
        reviewer_id: str,
        reviewer_role: str,
    ) -> RoleRequest | None:
        with get_connection() as connection:
            with connection.transaction():
                request_row = connection.execute(
                    f"""
                    SELECT {_SELECT_COLUMNS}
                    FROM user_role_requests
                    WHERE id = %s
                    FOR UPDATE
                    """,
                    (request_id,),
                ).fetchone()

                if request_row is None:
                    return None
                if request_row[4] != "pending":
                    raise ValueError(
                        "This role request has already been reviewed."
                    )

                role_row = connection.execute(
                    "SELECT id FROM roles WHERE name = %s",
                    (request_row[2],),
                ).fetchone()
                if role_row is None:
                    raise RuntimeError(
                        "The requested staff role is not configured."
                    )

                connection.execute(
                    """
                    UPDATE users
                    SET role_id = %s,
                        updated_at = CURRENT_TIMESTAMP,
                        updated_by = %s
                    WHERE id = %s
                    """,
                    (role_row[0], reviewer_id, request_row[1]),
                )

                approved_row = connection.execute(
                    f"""
                    UPDATE user_role_requests
                    SET status = 'approved',
                        reviewed_at = CURRENT_TIMESTAMP,
                        reviewed_by = %s
                    WHERE id = %s
                    RETURNING {_SELECT_COLUMNS}
                    """,
                    (reviewer_id, request_id),
                ).fetchone()

                self.audit_logs.record_on_connection(
                    connection,
                    actor_user_id=reviewer_id,
                    actor_role=reviewer_role,
                    action="user.role_request.approved",
                    target_type="role_request",
                    target_id=request_id,
                )

        return _to_entity(approved_row)

    def reject(
        self,
        request_id: str,
        reviewer_id: str,
        reviewer_role: str,
    ) -> RoleRequest | None:
        with get_connection() as connection:
            with connection.transaction():
                request_row = connection.execute(
                    f"""
                    SELECT {_SELECT_COLUMNS}
                    FROM user_role_requests
                    WHERE id = %s
                    FOR UPDATE
                    """,
                    (request_id,),
                ).fetchone()

                if request_row is None:
                    return None
                if request_row[4] != "pending":
                    raise ValueError(
                        "This role request has already been reviewed."
                    )

                rejected_row = connection.execute(
                    f"""
                    UPDATE user_role_requests
                    SET status = 'rejected',
                        reviewed_at = CURRENT_TIMESTAMP,
                        reviewed_by = %s
                    WHERE id = %s
                    RETURNING {_SELECT_COLUMNS}
                    """,
                    (reviewer_id, request_id),
                ).fetchone()

                self.audit_logs.record_on_connection(
                    connection,
                    actor_user_id=reviewer_id,
                    actor_role=reviewer_role,
                    action="user.role_request.rejected",
                    target_type="role_request",
                    target_id=request_id,
                )

        return _to_entity(rejected_row)
