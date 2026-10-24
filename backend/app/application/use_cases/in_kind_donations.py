from datetime import datetime, timezone
from uuid import uuid4

from app.application.interfaces.in_kind_donation import (
    InKindDonationRepository,
)
from app.application.schemas.in_kind_donation import (
    InKindDonationPledgeCreateRequest,
    InKindDonationStatusUpdateRequest,
)
from app.domain.entities.in_kind_donation import (
    InKindDonationPledge,
    InKindDonationStatus,
)
from app.domain.entities.user_context import Role, UserContext


_ORGANIZATION_STAFF_ROLES = {
    Role.DAYCARE_STAFF,
    Role.ORPHANAGE_STAFF,
    Role.CARE_HOME_STAFF,
}


class InKindDonationService:
    def __init__(self, repository: InKindDonationRepository):
        self.repository = repository

    @staticmethod
    def _authorize_donor(user: UserContext) -> None:
        if user.role != Role.DONOR_SUPPORTER:
            raise PermissionError(
                "Donor-supporter access is required"
            )

    def _authorize_organization_staff(
        self,
        user: UserContext,
        organization_id: str,
    ) -> None:
        role = user.organization_role_for(organization_id)
        if role not in _ORGANIZATION_STAFF_ROLES:
            raise PermissionError(
                "Organization staff access is required"
            )

        if not self.repository.is_authorized_organization_staff(
            organization_id,
            user.user_id,
            role,
        ):
            raise PermissionError(
                "You do not have permission to manage donations "
                "for this organization"
            )

    def create_pledge(
        self,
        user: UserContext,
        need_id: str,
        request: InKindDonationPledgeCreateRequest,
    ) -> InKindDonationPledge:
        self._authorize_donor(user)

        now = datetime.now(timezone.utc)

        pledge = InKindDonationPledge(
            id=str(uuid4()),
            need_id=need_id,
            donor_id=user.user_id,
            quantity=request.quantity,
            notes=request.notes,
            status=InKindDonationStatus.PLEDGED,
            created_at=now,
            updated_at=now,
        )

        return self.repository.create_pledge(
            pledge,
            user.user_id,
        )

    def list_my_pledges(
        self,
        user: UserContext,
    ) -> list[InKindDonationPledge]:
        self._authorize_donor(user)

        return self.repository.list_pledges_for_donor(
            user.user_id
        )

    def list_organization_pledges(
        self,
        user: UserContext,
        organization_id: str,
    ) -> list[InKindDonationPledge]:
        self._authorize_organization_staff(
            user,
            organization_id,
        )

        return self.repository.list_pledges_for_organization(
            organization_id
        )

    def update_pledge_status(
        self,
        user: UserContext,
        organization_id: str,
        pledge_id: str,
        request: InKindDonationStatusUpdateRequest,
    ) -> InKindDonationPledge:
        self._authorize_organization_staff(
            user,
            organization_id,
        )

        existing = self.repository.get_pledge_for_organization(
            organization_id,
            pledge_id,
        )

        if existing is None:
            raise LookupError(
                "Donation pledge not found for this organization"
            )

        allowed_next_status = {
            InKindDonationStatus.PLEDGED: (
                InKindDonationStatus.RECEIVED
            ),
            InKindDonationStatus.RECEIVED: (
                InKindDonationStatus.ALLOCATED
            ),
        }

        expected_next_status = allowed_next_status.get(
            existing.status
        )

        if request.status != expected_next_status:
            raise ValueError(
                f"Invalid pledge status transition: "
                f"{existing.status.value} to {request.status.value}"
            )

        updated = self.repository.transition_pledge_status(
            organization_id=organization_id,
            pledge_id=pledge_id,
            new_status=request.status,
            user_id=user.user_id,
            role=user.organization_role_for(organization_id),
        )

        if updated is None:
            raise LookupError(
                "Donation pledge not found for this organization"
            )

        return updated
