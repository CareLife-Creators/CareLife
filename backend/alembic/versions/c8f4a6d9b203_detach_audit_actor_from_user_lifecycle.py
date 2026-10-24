"""Keep audit history independent of user account retention."""

from typing import Sequence, Union

from alembic import op


revision: str = "c8f4a6d9b203"
down_revision: Union[str, Sequence[str], None] = (
    "e7a1c9d4f260"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "audit_logs_actor_user_id_fkey",
        "audit_logs",
        type_="foreignkey",
    )


def downgrade() -> None:
    op.create_foreign_key(
        "audit_logs_actor_user_id_fkey",
        "audit_logs",
        "users",
        ["actor_user_id"],
        ["id"],
        ondelete="RESTRICT",
    )
