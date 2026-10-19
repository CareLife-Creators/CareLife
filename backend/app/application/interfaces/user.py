from typing import Protocol

from app.domain.entities.user import User


class UserRepository(Protocol):
    def get_by_email(self, email: str) -> User | None:
        ...

    def get_by_id(self, user_id: str) -> User | None:
        ...

    def create(self, user: User) -> User:
        ...

    def create_if_not_exists(self, user: User) -> User | None:
        ...

    def update_profile(
        self,
        user_id: str,
        changes: dict[str, str | None],
    ) -> User | None:
        ...
