from datetime import date
from uuid import uuid4

from app.application.interfaces.user import UserRepository
from app.core.security import hash_password
from app.domain.entities.user import User


class SignupService:
    def __init__(
        self,
        repository: UserRepository,
    ):
        self.repository = repository

    def signup(
        self,
        username: str,
        email: str,
        date_of_birth: date,
        gender: str,
        password: str,
    ) -> User:
        normalized_email = email.strip().lower()
        normalized_username = username.strip()

        existing_user = self.repository.get_by_email(
            normalized_email
        )

        if existing_user is not None:
            raise ValueError(
                "An account with this email already exists"
            )

        user = User(
            id=str(uuid4()),
            username=normalized_username,
            email=normalized_email,
            date_of_birth=date_of_birth,
            gender=gender,
            password_hash=hash_password(password),
        )

        return self.repository.create(user)