"""Merge the caregiver and orphanage impact migration heads."""

from typing import Sequence, Union


revision: str = "a5f7c9d2e4b1"
down_revision: Union[str, Sequence[str], None] = (
    "d7f4b2a91c60",
    "b8c2d4e6f901",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Join the existing migration branches."""


def downgrade() -> None:
    """Keep both parent revisions applied when downgrading this merge point."""
