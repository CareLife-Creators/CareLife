from datetime import datetime

from app.infrastructure.database.connection import get_connection


class PostgresSessionRepository:
    def revoke_token(
        self,
        token_id: str,
        user_id: str,
        revoked_at: datetime,
        expires_at: datetime,
    ) -> None:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO revoked_tokens (
                    token_id,
                    user_id,
                    revoked_at,
                    expires_at
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (token_id)
                DO UPDATE SET
                    revoked_at = EXCLUDED.revoked_at,
                    expires_at = EXCLUDED.expires_at
                """,
                (
                    token_id,
                    user_id,
                    revoked_at,
                    expires_at,
                ),
            )
            connection.commit()

    def is_token_revoked(self, token_id: str) -> bool:
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM revoked_tokens
                WHERE token_id = %s
                  AND expires_at > NOW()
                LIMIT 1
                """,
                (token_id,),
            ).fetchone()

        return row is not None