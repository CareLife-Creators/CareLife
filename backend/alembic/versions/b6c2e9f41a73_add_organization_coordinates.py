"""Store organization map coordinates and join current migration heads."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b6c2e9f41a73"
down_revision: Union[str, Sequence[str], None] = "f84c2a1d7b90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("organizations", sa.Column("longitude", sa.Float(), nullable=True))
    op.create_check_constraint(
        "ck_organizations_coordinates_pair", "organizations",
        "(latitude IS NULL AND longitude IS NULL) OR "
        "(latitude BETWEEN 20.5 AND 26.8 AND longitude BETWEEN 88.0 AND 92.8)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_organizations_coordinates_pair", "organizations", type_="check")
    op.drop_column("organizations", "longitude")
    op.drop_column("organizations", "latitude")
