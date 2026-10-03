from datetime import date

from sqlalchemy import Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    username: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    date_of_birth: Mapped[date] = mapped_column(
        nullable=False,
    )

    gender: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ux_users_email_lower",
            func.lower(email),
            unique=True,
        ),
    )