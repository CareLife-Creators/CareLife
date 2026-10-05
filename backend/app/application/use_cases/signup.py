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
        email: str,
        password: str,
    ) -> User:
        normalized_email = email.strip().lower()

        existing_user = self.repository.get_by_email(
            normalized_email
        )

        if existing_user is not None:
            raise ValueError(
                "An account with this email already exists"
            )

        user = User(
            id=str(uuid4()),
            email=normalized_email,
            password_hash=hash_password(password),
            role_name="parent_guardian",
        )

        return self.repository.create(user)