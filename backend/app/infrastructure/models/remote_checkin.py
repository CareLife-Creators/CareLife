from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base


class ResidentFamilyConsentModel(Base):
    __tablename__ = "resident_family_consents"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    # The resident profile is handled by the separate
    # resident-profile ticket.
    resident_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    family_representative_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )

    granted_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    granted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    revoked_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

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

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'revoked')",
            name="ck_resident_family_consents_status",
        ),
        UniqueConstraint(
            "resident_id",
            "organization_id",
            "family_representative_id",
            name="uq_resident_family_consent",
        ),
        Index(
            "ix_resident_family_consents_resident",
            "resident_id",
            "status",
        ),
    )


class RemoteCheckInModel(Base):
    __tablename__ = "resident_remote_checkins"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    consent_id: Mapped[str] = mapped_column(
        ForeignKey(
            "resident_family_consents.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    resident_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    actor_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    wellbeing_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "wellbeing_status IN "
            "('well', 'needs_attention', 'urgent')",
            name="ck_remote_checkins_wellbeing_status",
        ),
        Index(
            "ix_remote_checkins_resident_recorded",
            "resident_id",
            "recorded_at",
        ),
    )