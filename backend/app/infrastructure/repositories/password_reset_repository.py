from datetime import datetime

from app.domain.entities.password_reset_token import (
    PasswordResetToken,
)
from app.infrastructure.database.connection import get_connection


class PostgresPasswordResetRepository:

    def get_user_by_email(
        self,
        email: str,
    ) -> dict | None:

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    id,
                    email,
                    password_hash
                FROM users
                WHERE LOWER(email) = LOWER(%s)
                LIMIT 1
                """,
                (email,),
            ).fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "email": row[1],
            "password_hash": row[2],
        }

    def create_token(
        self,
        token: PasswordResetToken,
    ) -> None:

        with get_connection() as connection:
            with connection.transaction():

                connection.execute(
                    """
                    DELETE FROM password_reset_tokens
                    WHERE user_id = %s
                      AND used_at IS NULL
                    """,
                    (token.user_id,),
                )

                connection.execute(
                    """
                    INSERT INTO password_reset_tokens (
                        user_id,
                        token_hash,
                        expires_at,
                        used_at
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        token.user_id,
                        token.token_hash,
                        token.expires_at,
                        token.used_at,
                    ),
                )

    def reset_password(
        self,
        token_hash: str,
        password_hash: str,
        now: datetime,
    ) -> bool:

        with get_connection() as connection:
            with connection.transaction():

                row = connection.execute(
                    """
                    SELECT
                        id,
                        user_id
                    FROM password_reset_tokens
                    WHERE token_hash = %s
                      AND used_at IS NULL
                      AND expires_at > %s
                    FOR UPDATE
                    """,
                    (
                        token_hash,
                        now,
                    ),
                ).fetchone()

                if row is None:
                    return False

                token_id = row[0]
                user_id = row[1]

                user_result = connection.execute(
                    """
                    UPDATE users
                    SET
                        password_hash = %s,
                        updated_at = CURRENT_TIMESTAMP,
                        updated_by = %s
                    WHERE id = %s
                    """,
                    (
                        password_hash,
                        user_id,
                        user_id,
                    ),
                )

                if user_result.rowcount != 1:
                    return False

                token_result = connection.execute(
                    """
                    UPDATE password_reset_tokens
                    SET used_at = %s
                    WHERE id = %s
                      AND used_at IS NULL
                    """,
                    (
                        now,
                        token_id,
                    ),
                )

                if token_result.rowcount != 1:
                    return False

        return True