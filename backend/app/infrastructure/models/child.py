from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base


class ChildModel(Base):
    __tablename__ = "children"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    parent_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    date_of_birth: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    gender: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    allergies: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    medical_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    orphanage_organization_id: Mapped[str | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
    )

    daycare_organization_id: Mapped[str | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"),
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


class OrphanageOutcomeModel(Base):
    __tablename__ = "orphanage_outcomes"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    child_id: Mapped[str] = mapped_column(
        ForeignKey("children.id", ondelete="CASCADE"),
        nullable=False,
    )

    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    outcome_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    outcome_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    outcome_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_by: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
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


class ChildContactModel(Base):
    __tablename__ = "child_contacts"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    child_id: Mapped[str] = mapped_column(
        ForeignKey("children.id", ondelete="CASCADE"),
        nullable=False,
    )

    contact_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    relationship_to_child: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    phone: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(254),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_by: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
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