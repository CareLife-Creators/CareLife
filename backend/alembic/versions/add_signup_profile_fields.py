"""add signup profile fields

Revision ID: add_signup_profile_fields
Revises: e5146543d555
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "add_signup_profile_fields"
down_revision: Union[str, Sequence[str], None] = "e5146543d555"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "username",
            sa.String(),
            nullable=False,
            server_default="user",
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "date_of_birth",
            sa.Date(),
            nullable=False,
            server_default=sa.text("'2000-01-01'"),
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "gender",
            sa.String(),
            nullable=False,
            server_default="Prefer not to say",
        ),
    )

    op.alter_column(
        "users",
        "username",
        server_default=None,
    )

    op.alter_column(
        "users",
        "date_of_birth",
        server_default=None,
    )

    op.alter_column(
        "users",
        "gender",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("users", "gender")
    op.drop_column("users", "date_of_birth")
    op.drop_column("users", "username")