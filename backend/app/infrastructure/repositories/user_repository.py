from app.domain.entities.user import User
from app.infrastructure.database.connection import get_connection
from app.infrastructure.repositories.audit_log_repository import PostgresAuditLogRepository


class PostgresUserRepository:
    audit_logs = PostgresAuditLogRepository()

    def list_users(self) -> list[dict]:
        """Return safe account summaries for the administrator directory."""
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT u.id, u.email, u.full_name, r.name, u.is_active,
                       u.created_at,
                       ARRAY(
                           SELECT uo.organization_id
                           FROM user_organizations uo
                           WHERE uo.user_id = u.id
                           ORDER BY uo.organization_id
                       ) AS organization_ids
                FROM users u
                JOIN roles r ON r.id = u.role_id
                ORDER BY u.created_at DESC, LOWER(u.email)
                """
            ).fetchall()
        return [
            {
                "user_id": row[0],
                "email": row[1],
                "full_name": row[2],
                "role": row[3],
                "is_active": row[4],
                "created_at": row[5],
                "organization_ids": row[6] or [],
            }
            for row in rows
        ]

    def create_admin(self, user: User, actor_user_id: str) -> User:
        with get_connection() as connection:
            with connection.transaction():
                connection.execute("SELECT pg_advisory_xact_lock(81420371)")
                connection.execute(
                    """INSERT INTO users (id, role_id, email, password_hash,
                       full_name, is_active, updated_by)
                       VALUES (%s, (SELECT id FROM roles WHERE name = %s),
                               %s, %s, %s, TRUE, %s)""",
                    (user.id, "carelife_admin", user.email, user.password_hash,
                     user.full_name, actor_user_id),
                )
                self.audit_logs.record_on_connection(
                    connection, actor_user_id=actor_user_id,
                    actor_role="carelife_admin", action="admin_account_created",
                    target_type="user", target_id=user.id,
                )
        return user

    def set_active(self, user_id: str, is_active: bool, actor_user_id: str) -> bool:
        with get_connection() as connection:
            with connection.transaction():
                connection.execute("SELECT pg_advisory_xact_lock(81420371)")
                target = connection.execute(
                    "SELECT u.is_active, r.name FROM users u JOIN roles r ON r.id=u.role_id WHERE u.id=%s FOR UPDATE",
                    (user_id,),
                ).fetchone()
                if target is None:
                    return False
                if bool(target[0]) == is_active:
                    return True
                if not is_active and target[1] == "carelife_admin":
                    active_admins = connection.execute(
                        "SELECT COUNT(*) FROM users u JOIN roles r ON r.id=u.role_id WHERE r.name='carelife_admin' AND u.is_active=TRUE"
                    ).fetchone()[0]
                    if active_admins <= 1:
                        raise ValueError("The last active CareLife admin cannot be deactivated.")
                connection.execute(
                    "UPDATE users SET is_active=%s, updated_at=CURRENT_TIMESTAMP, updated_by=%s WHERE id=%s",
                    (is_active, actor_user_id, user_id),
                )
                self.audit_logs.record_on_connection(
                    connection, actor_user_id=actor_user_id,
                    actor_role="carelife_admin",
                    action="user_deactivated" if not is_active else "user_reactivated",
                    target_type="user", target_id=user_id,
                )
        return True

    def get_by_email(
        self,
        email: str,
    ) -> User | None:

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    u.id,
                    u.email,
                    u.password_hash,
                    r.name,
                    u.full_name,
                    u.phone,
                    u.is_active
                FROM users u
                JOIN roles r
                    ON r.id = u.role_id
                WHERE LOWER(u.email) = LOWER(%s)
                LIMIT 1
                """,
                (email,),
            ).fetchone()

            if row is None:
                return None

            organization_rows = connection.execute(
                """
                SELECT organization_id
                FROM user_organizations
                WHERE user_id = %s
                ORDER BY organization_id
                """,
                (row[0],),
            ).fetchall()

        organization_ids = [
            organization_row[0]
            for organization_row in organization_rows
        ]

        return User(
            id=row[0],
            email=row[1],
            password_hash=row[2],
            role_name=row[3],
            organization_id=(
                organization_ids[0]
                if organization_ids
                else None
            ),
            organization_ids=organization_ids,
            full_name=row[4],
            phone=row[5],
            is_active=row[6],
        )

    def get_by_id(
        self,
        user_id: str,
    ) -> User | None:

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    u.id,
                    u.email,
                    u.password_hash,
                    r.name,
                    u.full_name,
                    u.phone,
                    u.is_active
                FROM users u
                JOIN roles r
                    ON r.id = u.role_id
                WHERE u.id = %s
                LIMIT 1
                """,
                (user_id,),
            ).fetchone()

            if row is None:
                return None

            organization_rows = connection.execute(
                """
                SELECT organization_id
                FROM user_organizations
                WHERE user_id = %s
                ORDER BY organization_id
                """,
                (user_id,),
            ).fetchall()

        organization_ids = [
            organization_row[0]
            for organization_row in organization_rows
        ]

        return User(
            id=row[0],
            email=row[1],
            password_hash=row[2],
            role_name=row[3],
            organization_id=(
                organization_ids[0]
                if organization_ids
                else None
            ),
            organization_ids=organization_ids,
            full_name=row[4],
            phone=row[5],
            is_active=row[6],
        )

    def update_profile(
        self,
        user_id: str,
        changes: dict[str, str | None],
    ) -> User | None:
        allowed_fields = {"full_name", "phone"}

        if not changes:
            raise ValueError(
                "At least one profile field must be provided."
            )

        if not set(changes).issubset(allowed_fields):
            raise ValueError(
                "Only full_name and phone can be updated."
            )

        assignments = [
            f"{field} = %s"
            for field in changes
        ]

        values = [
            changes[field]
            for field in changes
        ]

        assignments.extend([
            "updated_at = CURRENT_TIMESTAMP",
            "updated_by = %s",
        ])

        # Record the authenticated user as the updater.
        values.append(user_id)

        # Identify the profile that is being updated.
        values.append(user_id)

        with get_connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    f"""
                    UPDATE users
                    SET {", ".join(assignments)}
                    WHERE id = %s
                    RETURNING id
                    """,
                    values,
                ).fetchone()

        if row is None:
            return None

        return self.get_by_id(user_id)

    def create_if_not_exists(
        self,
        user: User,
    ) -> User | None:
        """Create a user unless the normalized email already exists.

        The database conflict handler closes the race between signup's
        lookup and insert without revealing whether the email is registered.
        """
        with get_connection() as connection:
            with connection.transaction():
                row = connection.execute(
                    """
                    INSERT INTO users (
                        id,
                        role_id,
                        email,
                        password_hash,
                        full_name,
                        phone,
                        is_active
                    )
                    VALUES (
                        %s,
                        (SELECT id FROM roles WHERE name = %s),
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    ON CONFLICT DO NOTHING
                    RETURNING id
                    """,
                    (
                        user.id,
                        user.role_name,
                        user.email,
                        user.password_hash,
                        user.full_name,
                        user.phone,
                        user.is_active,
                    ),
                ).fetchone()
        if row is None:
            return None
        return user

    def create(
        self,
        user: User,
    ) -> User:

        with get_connection() as connection:
            with connection.transaction():

                connection.execute(
                    """
                    INSERT INTO users (
                        id,
                        role_id,
                        email,
                        password_hash,
                        full_name,
                        phone,
                        is_active
                    )
                    VALUES (
                        %s,
                        (
                            SELECT id
                            FROM roles
                            WHERE name = %s
                        ),
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        user.id,
                        user.role_name,
                        user.email,
                        user.password_hash,
                        user.full_name,
                        user.phone,
                        user.is_active,
                    ),
                )

        return user
