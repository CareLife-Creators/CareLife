from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base


class InKindDonationPledgeModel(Base):
    __tablename__ = "in_kind_donation_pledges"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    need_id: Mapped[str] = mapped_column(
        ForeignKey("donation_needs.id", ondelete="RESTRICT"),
        nullable=False,
    )

    donor_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'pledged'"),
    )

    received_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )

    received_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    allocated_by: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )

    allocated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_in_kind_pledges_quantity_positive",
        ),
        CheckConstraint(
            "status IN ('pledged', 'received', 'allocated')",
            name="ck_in_kind_pledges_status",
        ),
        CheckConstraint(
            "(status = 'pledged' "
            "AND received_at IS NULL AND allocated_at IS NULL) "
            "OR (status = 'received' "
            "AND received_at IS NOT NULL AND allocated_at IS NULL) "
            "OR (status = 'allocated' "
            "AND received_at IS NOT NULL AND allocated_at IS NOT NULL)",
            name="ck_in_kind_pledges_status_timestamps",
        ),
        Index(
            "ix_in_kind_pledges_donor_created",
            "donor_id",
            "created_at",
        ),
        Index(
            "ix_in_kind_pledges_need_status_created",
            "need_id",
            "status",
            "created_at",
        ),
    )