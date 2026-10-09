from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base


class ImpactUpdateModel(Base):
    __tablename__ = "impact_updates"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default="pending_review",
    )

    created_by: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    reviewed_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )

    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending_review', 'approved', 'rejected')",
            name="ck_impact_updates_status",
        ),
        Index(
            "ix_impact_updates_org_status_created",
            "organization_id",
            "status",
            "created_at",
        ),
    )


class ImpactMediaModel(Base):
    __tablename__ = "impact_media"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    update_id: Mapped[str] = mapped_column(
        ForeignKey("impact_updates.id", ondelete="CASCADE"),
        nullable=False,
    )

    storage_key: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    media_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "media_type IN ('image', 'video')",
            name="ck_impact_media_type",
        ),
        CheckConstraint(
            "file_size > 0",
            name="ck_impact_media_file_size",
        ),
        Index("ix_impact_media_update", "update_id"),
    )