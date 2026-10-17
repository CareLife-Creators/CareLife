from typing import Protocol

from app.domain.entities.in_kind_donation import (
    InKindDonationPledge,
    InKindDonationStatus,
)
from app.domain.entities.user_context import Role


class InKindDonationRepository(Protocol):
    def is_authorized_organization_staff(
        self,
        organization_id: str,
        user_id: str,
        role: Role,
    ) -> bool: ...

    def create_pledge(
        self,
        pledge: InKindDonationPledge,
        donor_id: str,
    ) -> InKindDonationPledge: ...

    def list_pledges_for_donor(
        self,
        donor_id: str,
    ) -> list[InKindDonationPledge]: ...

    def get_pledge_for_donor(
        self,
        pledge_id: str,
        donor_id: str,
    ) -> InKindDonationPledge | None: ...

    def list_pledges_for_organization(
        self,
        organization_id: str,
    ) -> list[InKindDonationPledge]: ...

    def get_pledge_for_organization(
        self,
        organization_id: str,
        pledge_id: str,
    ) -> InKindDonationPledge | None: ...

    def transition_pledge_status(
        self,
        organization_id: str,
        pledge_id: str,
        new_status: InKindDonationStatus,
        user_id: str,
        role: Role,
    ) -> InKindDonationPledge | None: ...