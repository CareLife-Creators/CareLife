"""Create immutable administrative audit logs."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e7a1c9d4f260"
down_revision: Union[str, Sequence[str], None] = (
    "d2b48f7a6c10"
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column(
            "id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "actor_user_id",
            sa.String(),
            nullable=False,
        ),
        sa.Column(
            "actor_role",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "action",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "target_type",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "target_id",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_audit_logs_created_at",
        "audit_logs",
        ["created_at"],
    )

    op.create_index(
        "ix_audit_logs_target_created_at",
        "audit_logs",
        ["target_type", "target_id", "created_at"],
    )

    # Enforce append-only behavior at the database level.
    op.execute(
        """
        CREATE FUNCTION prevent_audit_log_mutation()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF TG_OP IN ('UPDATE', 'DELETE') THEN
                RAISE EXCEPTION
                    'Audit log records are immutable';
            END IF;

            RETURN NULL;
        END;
        $$;
        """
    )

    op.execute(
        """
        CREATE TRIGGER audit_logs_prevent_mutation
        BEFORE UPDATE OR DELETE ON audit_logs
        FOR EACH ROW
        EXECUTE FUNCTION prevent_audit_log_mutation();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TRIGGER IF EXISTS audit_logs_prevent_mutation
        ON audit_logs;
        """
    )

    op.drop_index(
        "ix_audit_logs_target_created_at",
        table_name="audit_logs",
    )

    op.drop_index(
        "ix_audit_logs_created_at",
        table_name="audit_logs",
    )

    op.drop_table("audit_logs")

    op.execute(
        """
        DROP FUNCTION IF EXISTS prevent_audit_log_mutation();
        """
    )