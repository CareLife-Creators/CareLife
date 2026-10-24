from datetime import datetime

from sqlalchemy import (
    DateTime,
    Index,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    # Historical identifier, intentionally not a user foreign key.
    actor_user_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    actor_role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    target_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    target_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_audit_logs_created_at",
            "created_at",
        ),
        Index(
            "ix_audit_logs_target_created_at",
            "target_type",
            "target_id",
            "created_at",
        ),
    )
