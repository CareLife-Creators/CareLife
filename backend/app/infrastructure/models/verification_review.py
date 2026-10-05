from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base


class VerificationReviewModel(Base):
    __tablename__ = "verification_reviews"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    organization_id: Mapped[str] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    reviewer_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    status_id: Mapped[int] = mapped_column(
        ForeignKey(
            "verification_statuses.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )