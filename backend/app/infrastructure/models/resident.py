from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base


class ResidentProfileModel(Base):
    __tablename__ = "resident_profiles"

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

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    preferred_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    room_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    emergency_contact_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    emergency_contact_phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="active",
    )

    created_by: Mapped[str] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    updated_by: Mapped[str] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
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
            "status IN ('active', 'inactive')",
            name="ck_resident_profiles_status",
        ),
        CheckConstraint(
            "(emergency_contact_name IS NULL) = "
            "(emergency_contact_phone IS NULL)",
            name="ck_resident_profiles_emergency_contact_pair",
        ),
        Index(
            "ix_resident_profiles_org_status_name",
            "organization_id",
            "status",
            "full_name",
        ),
    )