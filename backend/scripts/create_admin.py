"""Create the first CareLife administrator account interactively.

Run after applying database migrations:
    python -m scripts.create_admin

This command only creates a new account. It never changes an existing account's
role or password, and public signup cannot assign the administrator role.
"""

from getpass import getpass
import os
from uuid import uuid4

from app.core.security import hash_password
from app.infrastructure.database.connection import get_connection


def main() -> None:
    email = os.environ.get("CARELIFE_ADMIN_EMAIL") or input("Administrator email: ")
    full_name = os.environ.get("CARELIFE_ADMIN_NAME") or input("Full name: ")
    phone = os.environ.get("CARELIFE_ADMIN_PHONE")
    if phone is None:
        phone = input("Phone number: ")
    password = os.environ.get("CARELIFE_ADMIN_PASSWORD") or getpass(
        "Password (at least 8 characters): "
    )
    confirmation = os.environ.get("CARELIFE_ADMIN_CONFIRM") or getpass(
        "Confirm password: "
    )

    email = email.strip().lower()
    full_name = full_name.strip()
    phone = phone.strip()

    if not email or "@" not in email:
        raise SystemExit("Enter a valid email address.")
    if not full_name:
        raise SystemExit("Full name is required.")
    if len(password) < 8:
        raise SystemExit("Use a password with at least 8 characters.")
    if password != confirmation:
        raise SystemExit("Passwords do not match.")

    with get_connection() as connection:
        with connection.transaction():
            existing = connection.execute(
                "SELECT id FROM users WHERE LOWER(email) = LOWER(%s) LIMIT 1",
                (email,),
            ).fetchone()
            if existing:
                raise SystemExit(
                    "That email already has an account. No account was changed."
                )

            admin_role = connection.execute(
                "SELECT id FROM roles WHERE name = 'carelife_admin' LIMIT 1"
            ).fetchone()
            if not admin_role:
                raise SystemExit(
                    "The administrator role is missing. Apply database migrations first."
                )

            created = connection.execute(
                """
                INSERT INTO users (
                    id, role_id, email, password_hash, full_name, phone, is_active
                )
                VALUES (
                    %s,
                    %s, %s, %s, %s, %s, TRUE
                )
                RETURNING id
                """,
                (str(uuid4()), admin_role[0], email, hash_password(password), full_name, phone),
            ).fetchone()
            if not created:
                raise RuntimeError("Administrator account could not be created.")

    print("CareLife administrator account created. Sign in with the entered email and password.")


if __name__ == "__main__":
    main()
