from typing import Protocol

from app.domain.entities.resident import (
    ResidentProfile,
    ResidentProfileStatus,
)
from app.domain.entities.user_context import UserContext


class ResidentProfileRepository(Protocol):

    def create_profile(
        self,
        user: UserContext,
        organization_id: str,
        values: dict[str, object],
    ) -> ResidentProfile:
        ...

    def list_profiles(
        self,
        user: UserContext,
        organization_id: str,
        profile_status: ResidentProfileStatus | None = None,
    ) -> list[ResidentProfile]:
        ...

    def get_profile(
        self,
        user: UserContext,
        organization_id: str,
        resident_id: str,
    ) -> ResidentProfile | None:
        ...

    def update_profile(
        self,
        user: UserContext,
        organization_id: str,
        resident_id: str,
        changes: dict[str, object],
    ) -> ResidentProfile | None:
        ...