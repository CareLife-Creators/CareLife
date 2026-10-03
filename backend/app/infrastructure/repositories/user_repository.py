from app.domain.entities.user import User
from app.infrastructure.database.connection import get_connection
from app.infrastructure.database.schema import initialize_schema


class PostgresUserRepository:
    def __init__(self):
        initialize_schema()

    def get_by_email(self, email: str) -> User | None:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, email, password_hash
                FROM users
                WHERE LOWER(email) = LOWER(%s)
                LIMIT 1
                """,
                (email,),
            ).fetchone()

        if row is None:
            return None

        return User(
            id=row[0],
            email=row[1],
            password_hash=row[2],
        )

    def create(self, user: User) -> User:
        with get_connection() as connection:
            with connection.transaction():
                connection.execute(
                    """
                    INSERT INTO users (
                        id,
                        email,
                        password_hash
                    )
                    VALUES (%s, %s, %s)
                    """,
                    (
                        user.id,
                        user.email,
                        user.password_hash,
                    ),
                )

        return user