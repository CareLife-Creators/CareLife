from getpass import getpass
from uuid import uuid4

from app.core.security import hash_password
from app.infrastructure.database.connection import get_connection
from app.infrastructure.database.schema import initialize_schema


def main():
    initialize_schema()

    email = input("Email: ").strip().lower()
    password = getpass("Password: ")

    user_id = str(uuid4())
    password_hash = hash_password(password)

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
                ON CONFLICT DO NOTHING
                """,
                (
                    user_id,
                    email,
                    password_hash,
                ),
            )

    print("Development user created or already exists.")


if __name__ == "__main__":
    main()