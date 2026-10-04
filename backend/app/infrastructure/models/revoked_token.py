from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base


class RevokedTokenModel(Base):
    __tablename__ = "revoked_tokens"

    token_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_revoked_tokens_user",
            "user_id",
        ),
        Index(
            "ix_revoked_tokens_expires",
            "expires_at",
        ),
    )