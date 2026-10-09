from app.application.interfaces.user import UserRepository
from app.core.security import verify_password
from app.domain.entities.user import User


class LoginService:
    def __init__(
        self,
        repository: UserRepository,
    ):
        self.repository = repository

    def login(
        self,
        email: str,
        password: str,
    ) -> User:
        normalized_email = email.strip().lower()

        user = self.repository.get_by_email(
            normalized_email
        )

        if user is None:
            raise ValueError("Invalid email or password")

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Invalid email or password")

        return user