from typing import Protocol

from app.domain.entities.donation import DonationCampaign, DonationNeed
from app.domain.entities.user_context import Role


class DonationRepository(Protocol):
    def is_authorized_organization_staff(
        self, organization_id: str, user_id: str, role: Role
    ) -> bool: ...

    def create_campaign(
        self, campaign: DonationCampaign, user_id: str, role: Role
    ) -> DonationCampaign: ...

    def get_campaign_for_organization(
        self, organization_id: str, campaign_id: str
    ) -> DonationCampaign | None: ...

    def list_campaigns_for_organization(
        self, organization_id: str
    ) -> list[DonationCampaign]: ...

    def update_campaign(
        self,
        organization_id: str,
        campaign_id: str,
        changes: dict[str, object],
        user_id: str,
        role: Role,
    ) -> DonationCampaign | None: ...

    def list_public_campaigns(
        self, organization_id: str | None = None
    ) -> list[DonationCampaign]: ...

    def get_public_campaign(self, campaign_id: str) -> DonationCampaign | None: ...

    def create_need(
        self, need: DonationNeed, user_id: str, role: Role
    ) -> DonationNeed: ...

    def get_need_for_organization(
        self, organization_id: str, need_id: str
    ) -> DonationNeed | None: ...

    def list_needs_for_organization(
        self, organization_id: str
    ) -> list[DonationNeed]: ...

    def update_need(
        self,
        organization_id: str,
        need_id: str,
        changes: dict[str, object],
        user_id: str,
        role: Role,
    ) -> DonationNeed | None: ...

    def list_public_needs(
        self, organization_id: str | None = None
    ) -> list[DonationNeed]: ...

    def get_public_need(self, need_id: str) -> DonationNeed | None: ...
