from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base


class OrganizationVerificationModel(Base):
    __tablename__ = "organization_verifications"

    organization_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    organization_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    organization_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    message: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'expired')",
            name="ck_organization_verifications_status",
        ),
    )