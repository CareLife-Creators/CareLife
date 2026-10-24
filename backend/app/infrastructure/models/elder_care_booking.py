from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base


class ElderCareBookingModel(Base):
    __tablename__ = "elder_care_bookings"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    resident_id: Mapped[str] = mapped_column(
        ForeignKey(
            "resident_profiles.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    requester_user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    provider_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    caregiver_user_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "caregiver_profiles.user_id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    organization_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "organizations.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    availability_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "caregiver_availability.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    service_type: Mapped[str] = mapped_column(
        String(100),
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
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    cancelled_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
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
            name="ck_elder_care_bookings_time_range",
        ),
        CheckConstraint(
            "status IN "
            "('requested', 'approved', 'rejected', "
            "'cancelled', 'completed')",
            name="ck_elder_care_bookings_status",
        ),
        CheckConstraint(
            "(provider_type = 'caregiver' "
            "AND caregiver_user_id IS NOT NULL "
            "AND organization_id IS NULL "
            "AND availability_id IS NOT NULL) "
            "OR "
            "(provider_type = 'care_home' "
            "AND caregiver_user_id IS NULL "
            "AND organization_id IS NOT NULL "
            "AND availability_id IS NULL)",
            name="ck_elder_care_bookings_provider",
        ),
        Index(
            "ix_elder_care_bookings_resident_start",
            "resident_id",
            "starts_at",
        ),
        Index(
            "ix_elder_care_bookings_caregiver_status_start",
            "caregiver_user_id",
            "status",
            "starts_at",
        ),
        Index(
            "ix_elder_care_bookings_organization_status_start",
            "organization_id",
            "status",
            "starts_at",
        ),
        Index(
            "ix_elder_care_bookings_requester_created",
            "requester_user_id",
            "created_at",
        ),
    )


class ElderCareBookingStatusHistoryModel(Base):
    __tablename__ = "elder_care_booking_status_history"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    booking_id: Mapped[str] = mapped_column(
        ForeignKey(
            "elder_care_bookings.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    sequence_no: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    from_status: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    to_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    changed_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "to_status IN "
            "('requested', 'approved', 'rejected', "
            "'cancelled', 'completed')",
            name="ck_elder_care_booking_history_to_status",
        ),
        CheckConstraint(
            "from_status IS NULL OR from_status IN "
            "('requested', 'approved', 'rejected', "
            "'cancelled', 'completed')",
            name="ck_elder_care_booking_history_from_status",
        ),
        UniqueConstraint(
            "booking_id",
            "sequence_no",
            name="uq_elder_care_booking_history_sequence",
        ),
    )