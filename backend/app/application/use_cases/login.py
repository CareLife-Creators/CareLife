from app.application.interfaces.login import LoginRepository
from app.core.security import create_access_token, verify_password


class LoginService:
    def __init__(self, repository: LoginRepository):
        self.repository = repository

    def login(self, email: str, password: str) -> str:
        normalized_email = email.strip().lower()
        user = self.repository.get_user_by_email(normalized_email)

        if user is None or not verify_password(
            password,
            user["password_hash"],
        ):
            raise ValueError("Invalid email or password.")

        return create_access_token(user["id"])
