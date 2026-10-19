from uuid import uuid4

from app.application.interfaces.user import UserRepository
from app.core.security import hash_password
from app.domain.entities.user import User


PUBLIC_SIGNUP_ROLES = frozenset({
    "parent_guardian",
    "donor_supporter",
    "independent_caregiver",
    "family_representative",
})


class SignupService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def signup(
        self,
        email: str,
        password: str,
        full_name: str,
        phone: str,
        role: str,
    ) -> User | None:
        normalized_email = email.strip().lower()
        normalized_name = full_name.strip()

        # Enforce this in the application layer as well as the request
        # schema so internal callers cannot self-assign privileged roles.
        if role not in PUBLIC_SIGNUP_ROLES:
            raise ValueError("Invalid signup role")
        if not normalized_name:
            raise ValueError("Full name is required")

        if self.repository.get_by_email(normalized_email) is not None:
            return None

        user = User(
            id=str(uuid4()),
            email=normalized_email,
            password_hash=hash_password(password),
            role_name=role,
            full_name=normalized_name,
            phone=phone.strip(),
        )

        # Uses INSERT ... ON CONFLICT DO NOTHING to also handle concurrent
        # duplicate signups with the same generic HTTP response.
        return self.repository.create_if_not_exists(user)
