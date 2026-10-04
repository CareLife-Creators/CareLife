"""create core CareLife tables

Revision ID: a66dca08b27f
Revises:
Create Date: 2026-10-04 22:06:54.849802
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a66dca08b27f"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "verification_statuses",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "role_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "password_hash",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "full_name",
            sa.String(length=200),
            nullable=True,
        ),
        sa.Column(
            "phone",
            sa.String(length=30),
            nullable=True,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_by",
            sa.String(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ux_users_email_lower",
        "users",
        [sa.literal_column("lower(email)")],
        unique=True,
    )

    op.create_table(
        "organizations",
        sa.Column(
            "id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=200),
            nullable=False,
        ),
        sa.Column(
            "organization_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "status_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "submitted_by",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "location",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "contact",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_by",
            sa.String(),
            nullable=True,
        ),
        sa.CheckConstraint(
            "organization_type IN "
            "('daycare', 'orphanage', 'elderly_care')",
            name="ck_organizations_type",
        ),
        sa.ForeignKeyConstraint(
            ["status_id"],
            ["verification_statuses.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["submitted_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "password_reset_tokens",
        sa.Column(
            "id",
            sa.BigInteger(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "token_hash",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "used_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )

    op.create_index(
        "ix_password_reset_tokens_hash",
        "password_reset_tokens",
        ["token_hash"],
        unique=False,
    )

    op.create_index(
        "ix_password_reset_tokens_user",
        "password_reset_tokens",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "revoked_tokens",
        sa.Column(
            "token_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("token_id"),
    )

    op.create_index(
        "ix_revoked_tokens_expires",
        "revoked_tokens",
        ["expires_at"],
        unique=False,
    )

    op.create_index(
        "ix_revoked_tokens_user",
        "revoked_tokens",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "organization_documents",
        sa.Column(
            "id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "document_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "document_number",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "file_ref",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_by",
            sa.String(),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "user_organizations",
        sa.Column(
            "user_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "user_id",
            "organization_id",
        ),
    )

    op.create_table(
        "verification_reviews",
        sa.Column(
            "id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "reviewer_id",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "status_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "reviewed_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["reviewer_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["status_id"],
            ["verification_statuses.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.bulk_insert(
        sa.table(
            "roles",
            sa.column(
                "name",
                sa.String(length=50),
            ),
        ),
        [
            {"name": "carelife_admin"},
            {"name": "parent_guardian"},
            {"name": "daycare_staff"},
            {"name": "independent_caregiver"},
            {"name": "donor_supporter"},
            {"name": "orphanage_staff"},
            {"name": "family_representative"},
            {"name": "care_home_staff"},
        ],
    )

    op.bulk_insert(
        sa.table(
            "verification_statuses",
            sa.column(
                "name",
                sa.String(length=50),
            ),
        ),
        [
            {"name": "pending"},
            {"name": "under_review"},
            {"name": "verified"},
            {"name": "rejected"},
            {"name": "needs_correction"},
            {"name": "expired"},
            {"name": "suspended"},
        ],
    )


def downgrade() -> None:
    op.drop_table("verification_reviews")

    op.drop_table("user_organizations")

    op.drop_table("organization_documents")

    op.drop_index(
        "ix_revoked_tokens_user",
        table_name="revoked_tokens",
    )

    op.drop_index(
        "ix_revoked_tokens_expires",
        table_name="revoked_tokens",
    )

    op.drop_table("revoked_tokens")

    op.drop_index(
        "ix_password_reset_tokens_user",
        table_name="password_reset_tokens",
    )

    op.drop_index(
        "ix_password_reset_tokens_hash",
        table_name="password_reset_tokens",
    )

    op.drop_table("password_reset_tokens")

    op.drop_table("organizations")

    op.drop_index(
        "ux_users_email_lower",
        table_name="users",
    )

    op.drop_table("users")

    op.drop_table("verification_statuses")

    op.drop_table("roles")