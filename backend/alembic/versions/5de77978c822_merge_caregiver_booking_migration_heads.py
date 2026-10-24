"""Merge caregiver booking migration heads

Revision ID: 5de77978c822
Revises: f2c8a6d90134, f9b2c6d81470
Create Date: 2026-10-19 18:44:31.876644
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '5de77978c822'
down_revision: Union[str, Sequence[str], None] = ('f2c8a6d90134', 'f9b2c6d81470')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass