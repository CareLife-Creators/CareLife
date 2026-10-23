from app.application.interfaces.user import UserRepository
from app.domain.entities.user import User


class UserProfileService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def list_users(self) -> list[dict]:
        return self.repository.list_users()

    def create_admin(self, email: str, full_name: str, password: str, actor_user_id: str) -> User:
        from uuid import uuid4
        from app.core.security import hash_password
        normalized_email = email.strip().lower()
        normalized_name = full_name.strip()
        if not normalized_name:
            raise ValueError("Full name is required.")
        if self.repository.get_by_email(normalized_email) is not None:
            raise ValueError("An account with this email already exists.")
        user = User(id=str(uuid4()), email=normalized_email,
                    password_hash=hash_password(password), role_name="carelife_admin",
                    full_name=normalized_name)
        return self.repository.create_admin(user, actor_user_id)

    def set_user_active(self, user_id: str, is_active: bool, actor_user_id: str) -> bool:
        if user_id == actor_user_id and not is_active:
            raise ValueError("You cannot deactivate your own account.")
        return self.repository.set_active(user_id, is_active, actor_user_id)

    def get_profile(self, user_id: str) -> User:
        user = self.repository.get_by_id(user_id)

        if user is None or not user.is_active:
            raise LookupError("User profile not found.")

        return user

    def update_profile(
        self,
        user_id: str,
        changes: dict[str, str | None],
    ) -> User:
        allowed_fields = {"full_name", "phone"}

        if not changes:
            raise ValueError(
                "At least one profile field must be provided."
            )

        if not set(changes).issubset(allowed_fields):
            raise ValueError(
                "Only full_name and phone can be updated."
            )

        # Check the account before performing the update.
        current_user = self.repository.get_by_id(user_id)

        if current_user is None or not current_user.is_active:
            raise LookupError("User profile not found.")

        updated_user = self.repository.update_profile(
            user_id,
            changes,
        )

        if updated_user is None or not updated_user.is_active:
            raise LookupError("User profile not found.")

        return updated_user
