"""Add direct messaging conversations and messages."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f2c8a6d90134"
down_revision: Union[str, Sequence[str], None] = "c8f4a6d9b203"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column(
            "participant_one_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "participant_two_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "last_message_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.CheckConstraint(
            "participant_one_id < participant_two_id",
            name="ck_conversations_participant_order",
        ),
        sa.ForeignKeyConstraint(
            ["participant_one_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["participant_two_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "participant_one_id",
            "participant_two_id",
            name="uq_conversations_participants",
        ),
    )

    op.create_index(
        "ix_conversations_participant_one_recent",
        "conversations",
        ["participant_one_id", "last_message_at"],
    )

    op.create_index(
        "ix_conversations_participant_two_recent",
        "conversations",
        ["participant_two_id", "last_message_at"],
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("conversation_id", sa.String(), nullable=False),
        sa.Column("sender_user_id", sa.String(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(trim(body)) > 0",
            name="ck_messages_body_not_empty",
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["sender_user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_messages_conversation_created",
        "messages",
        ["conversation_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_messages_conversation_created",
        table_name="messages",
    )
    op.drop_table("messages")

    op.drop_index(
        "ix_conversations_participant_two_recent",
        table_name="conversations",
    )
    op.drop_index(
        "ix_conversations_participant_one_recent",
        table_name="conversations",
    )
    op.drop_table("conversations")