"""add daycare enrollment requests

Revision ID: d1e4f6a8b2c0
Revises: c9d7a1f0b3e2
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d1e4f6a8b2c0"
down_revision: Union[str, Sequence[str], None] = (
    "c9d7a1f0b3e2"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "organizations",
        sa.Column(
            "capacity",
            sa.Integer(),
            server_default=sa.text("20"),
            nullable=False,
        ),
    )

    op.create_check_constraint(
        "ck_organizations_capacity",
        "organizations",
        "capacity >= 0",
    )

    op.create_table(
        "daycare_enrollments",
        sa.Column(
            "id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "child_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "daycare_organization_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "reviewed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "reviewed_by",
            sa.String(),
            nullable=True,
        ),
        sa.Column(
            "cancelled_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "decision_message",
            sa.Text(),
            nullable=True,
        ),
        sa.CheckConstraint(
            "status IN "
            "('pending', 'approved', 'rejected', "
            "'waitlisted', 'cancelled')",
            name="ck_daycare_enrollment_status",
        ),
        sa.ForeignKeyConstraint(
            ["child_id"],
            ["children.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["daycare_organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["reviewed_by"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_daycare_enrollments_child",
        "daycare_enrollments",
        ["child_id"],
    )

    op.create_index(
        "ix_daycare_enrollments_daycare_status",
        "daycare_enrollments",
        [
            "daycare_organization_id",
            "status",
        ],
    )

    op.execute(
        """
        CREATE UNIQUE INDEX
        ux_daycare_enrollments_active_child_daycare
        ON daycare_enrollments (
            child_id,
            daycare_organization_id
        )
        WHERE status IN (
            'pending',
            'waitlisted',
            'approved'
        )
        """
    )


def downgrade() -> None:

    op.execute(
        """
        DROP INDEX
        IF EXISTS ux_daycare_enrollments_active_child_daycare
        """
    )

    op.drop_index(
        "ix_daycare_enrollments_daycare_status",
        table_name="daycare_enrollments",
    )

    op.drop_index(
        "ix_daycare_enrollments_child",
        table_name="daycare_enrollments",
    )

    op.drop_table("daycare_enrollments")

    op.drop_constraint(
        "ck_organizations_capacity",
        "organizations",
        type_="check",
    )

    op.drop_column(
        "organizations",
        "capacity",
    )