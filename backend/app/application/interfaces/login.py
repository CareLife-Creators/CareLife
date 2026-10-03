from typing import Protocol


class LoginRepository(Protocol):
    def get_user_by_email(self, email: str) -> dict | None:
        ...
