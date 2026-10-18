from typing import Protocol

from app.domain.entities.remote_checkin import (
    RemoteCheckIn,
    ResidentConsent,
)
from app.domain.entities.user_context import UserContext


class RemoteCheckInRepository(Protocol):

    def set_consent(
        self,
        user: UserContext,
        organization_id: str,
        resident_id: str,
        family_representative_id: str,
        consent_granted: bool,
    ) -> ResidentConsent:
        ...

    def create_checkin(
        self,
        actor_user_id: str,
        resident_id: str,
        wellbeing_status: str,
        notes: str | None,
    ) -> RemoteCheckIn:
        ...

    def list_checkins(
        self,
        user: UserContext,
        resident_id: str,
    ) -> list[RemoteCheckIn]:
        ...