from app.infrastructure.database.connection import get_connection


def initialize_schema() -> None:
    statements = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL
        );
        """,
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_users_email_lower
        ON users (LOWER(email));
        """,
        """
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id BIGSERIAL PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token_hash TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMPTZ NOT NULL,
            used_at TIMESTAMPTZ NULL
        );
        """,
        """
        CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_hash
        ON password_reset_tokens(token_hash);
        """,
        """
        CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_user
        ON password_reset_tokens(user_id);
        """,
    ]

    with get_connection() as connection:
        with connection.transaction():
            for statement in statements:
                connection.execute(statement)