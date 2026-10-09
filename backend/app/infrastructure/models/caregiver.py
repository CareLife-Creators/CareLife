
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
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base


class CaregiverProfileModel(Base):
    __tablename__ = "caregiver_profiles"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    service_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    experience_years: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'pending'"),
    )

    review_message: Mapped[str | None] = mapped_column(
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
            "service_type IN ('nanny', 'elder_care_giver')",
            name="ck_caregiver_profiles_service_type",
        ),
        CheckConstraint(
            "experience_years >= 0",
            name="ck_caregiver_profiles_experience_years",
        ),
        CheckConstraint(
            "verification_status IN ('pending', 'approved', 'rejected')",
            name="ck_caregiver_profiles_verification_status",
        ),
    )


class CaregiverDocumentModel(Base):
    __tablename__ = "caregiver_documents"

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

    document_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    document_reference: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "document_type IN ('identity', 'qualification')",
            name="ck_caregiver_documents_type",
        ),
        Index(
            "ix_caregiver_documents_user",
            "caregiver_user_id",
        ),
    )