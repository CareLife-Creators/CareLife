"""Add organization profile service-information fields."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7d4e9a2c681"
down_revision: Union[str, Sequence[str], None] = (
    "a5f7c9d2e4b1"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add optional service details to existing organizations."""

    op.add_column(
        "organizations",
        sa.Column(
            "age_range",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "organizations",
        sa.Column(
            "opening_hours",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "organizations",
        sa.Column(
            "facilities",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "organizations",
        sa.Column(
            "fees",
            sa.Text(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove only the columns introduced by this migration."""

    op.drop_column("organizations", "fees")
    op.drop_column("organizations", "facilities")
    op.drop_column("organizations", "opening_hours")
    op.drop_column("organizations", "age_range")