from app.application.interfaces.user import UserRepository
from app.domain.entities.user import User


class UserProfileService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

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