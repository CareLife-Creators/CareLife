from app.application.interfaces.remote_checkin import (
    RemoteCheckInRepository,
)
from app.application.schemas.remote_checkin import (
    ConsentUpdateRequest,
    RemoteCheckInCreateRequest,
)
from app.domain.entities.remote_checkin import (
    RemoteCheckIn,
    ResidentConsent,
)
from app.domain.entities.user_context import Role, UserContext


class RemoteCheckInService:

    def __init__(
        self,
        repository: RemoteCheckInRepository,
    ):
        self.repository = repository

    def set_consent(
        self,
        user: UserContext,
        organization_id: str,
        resident_id: str,
        request: ConsentUpdateRequest,
    ) -> ResidentConsent:
        if user.role not in {
            Role.CARE_HOME_STAFF,
            Role.CARELIFE_ADMIN,
        }:
            raise PermissionError(
                "Care-home staff or administrator access required"
            )

        return self.repository.set_consent(
            user=user,
            organization_id=organization_id,
            resident_id=resident_id,
            family_representative_id=(
                request.family_representative_id
            ),
            consent_granted=request.consent_granted,
        )

    def create_checkin(
        self,
        user: UserContext,
        resident_id: str,
        request: RemoteCheckInCreateRequest,
    ) -> RemoteCheckIn:
        if user.role != Role.FAMILY_REPRESENTATIVE:
            raise PermissionError(
                "Family representative access required"
            )

        return self.repository.create_checkin(
            actor_user_id=user.user_id,
            resident_id=resident_id,
            wellbeing_status=request.wellbeing_status.value,
            notes=request.notes,
        )

    def list_checkins(
        self,
        user: UserContext,
        resident_id: str,
    ) -> list[RemoteCheckIn]:
        if user.role not in {
            Role.FAMILY_REPRESENTATIVE,
            Role.CARE_HOME_STAFF,
            Role.CARELIFE_ADMIN,
        }:
            raise PermissionError(
                "You do not have permission to view these check-ins"
            )

        return self.repository.list_checkins(
            user=user,
            resident_id=resident_id,
        )