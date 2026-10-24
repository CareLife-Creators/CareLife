"""Track delivery of organization license expiry emails."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f3a8c1d6e902"
down_revision: Union[str, Sequence[str], None] = "b6c2e9f41a73"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "notifications",
        sa.Column("email_sent_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "notifications",
        sa.Column("document_type", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "notifications",
        sa.Column("document_expires_at", sa.Date(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("notifications", "document_expires_at")
    op.drop_column("notifications", "document_type")
    op.drop_column("notifications", "email_sent_at")
