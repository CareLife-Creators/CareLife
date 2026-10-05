from app.domain.entities.user import User
from app.infrastructure.database.connection import get_connection


class PostgresUserRepository:

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