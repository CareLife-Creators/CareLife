from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base


class CaregiverAvailabilityModel(Base):
    __tablename__ = "caregiver_availability"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    caregiver_user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "caregiver_profiles.user_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    ends_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "ends_at > starts_at",
            name="ck_caregiver_availability_time_range",
        ),
        Index(
            "ix_caregiver_availability_caregiver_start",
            "caregiver_user_id",
            "starts_at",
        ),
    )


class CaregiverAppointmentModel(Base):
    __tablename__ = "caregiver_appointments"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    availability_id: Mapped[str] = mapped_column(
        ForeignKey(
            "caregiver_availability.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    caregiver_user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "caregiver_profiles.user_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    requester_user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    service_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    ends_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'requested'"),
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    decision_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    reviewed_by: Mapped[str | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
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
            "ends_at > starts_at",
            name="ck_caregiver_appointments_time_range",
        ),
        CheckConstraint(
            "status IN ('requested', 'accepted', 'rejected')",
            name="ck_caregiver_appointments_status",
        ),
        Index(
            "ix_caregiver_appointments_requester",
            "requester_user_id",
            "created_at",
        ),
        Index(
            "ix_caregiver_appointments_caregiver",
            "caregiver_user_id",
            "starts_at",
        ),
        Index(
            "uq_caregiver_appointment_active_slot",
            "availability_id",
            unique=True,
            postgresql_where=text(
                "status IN ('requested', 'accepted')"
            ),
        ),
    )