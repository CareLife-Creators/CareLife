from datetime import datetime, timezone
from uuid import uuid4

from pydantic import ValidationError

from app.application.interfaces.donation import DonationRepository
from app.application.schemas.donation import (
    DonationCampaignCreateRequest,
    DonationCampaignUpdateRequest,
    DonationNeedCreateRequest,
    DonationNeedUpdateRequest,
)
from app.domain.entities.donation import DonationCampaign, DonationNeed
from app.domain.entities.user_context import Role, UserContext


_ORGANIZATION_STAFF_ROLES = {
    Role.DAYCARE_STAFF,
    Role.ORPHANAGE_STAFF,
    Role.CARE_HOME_STAFF,
}


class DonationService:
    def __init__(self, repository: DonationRepository):
        self.repository = repository

    def _authorize_organization_staff(self, user: UserContext, organization_id: str) -> None:
        if user.role not in _ORGANIZATION_STAFF_ROLES:
            raise PermissionError("Organization staff access required")
        if organization_id not in user.organization_ids and user.organization_id != organization_id:
            raise PermissionError("You do not have access to this organization")
        if not self.repository.is_authorized_organization_staff(
            organization_id, user.user_id, user.role
        ):
            raise PermissionError("You do not have permission to manage donations for this organization")

    def create_campaign(self, user: UserContext, organization_id: str, request: DonationCampaignCreateRequest) -> DonationCampaign:
        self._authorize_organization_staff(user, organization_id)
        now = datetime.now(timezone.utc)
        campaign = DonationCampaign(
            id=str(uuid4()), organization_id=organization_id,
            title=request.title, description=request.description,
            target_amount=request.target_amount, currency=request.currency,
            received_amount=0, utilized_amount=0,
            remaining_amount=request.target_amount, is_active=request.is_active,
            created_at=now, updated_at=now,
        )
        return self.repository.create_campaign(campaign, user.user_id, user.role)

    def list_organization_campaigns(self, user: UserContext, organization_id: str) -> list[DonationCampaign]:
        self._authorize_organization_staff(user, organization_id)
        return self.repository.list_campaigns_for_organization(organization_id)

    def update_campaign(self, user: UserContext, organization_id: str, campaign_id: str, request: DonationCampaignUpdateRequest) -> DonationCampaign:
        self._authorize_organization_staff(user, organization_id)
        if self.repository.get_campaign_for_organization(organization_id, campaign_id) is None:
            raise LookupError("Campaign not found for this organization")
        changes = request.model_dump(exclude_unset=True)
        for field in ("title", "target_amount", "currency", "utilized_amount", "is_active"):
            if field in changes and changes[field] is None:
                raise ValueError(f"{field} cannot be null")
        updated = self.repository.update_campaign(organization_id, campaign_id, changes, user.user_id, user.role)
        if updated is None:
            raise LookupError("Campaign not found for this organization")
        return updated

    def list_public_campaigns(self, organization_id: str | None = None) -> list[DonationCampaign]:
        return self.repository.list_public_campaigns(organization_id)

    def get_public_campaign(self, campaign_id: str) -> DonationCampaign:
        campaign = self.repository.get_public_campaign(campaign_id)
        if campaign is None:
            raise LookupError("Active campaign not found")
        return campaign

    def create_need(self, user: UserContext, organization_id: str, request: DonationNeedCreateRequest) -> DonationNeed:
        self._authorize_organization_staff(user, organization_id)
        now = datetime.now(timezone.utc)
        need = DonationNeed(
            id=str(uuid4()), organization_id=organization_id,
            title=request.title, description=request.description,
            category=request.category, need_type=request.need_type,
            target_amount=request.target_amount, target_quantity=request.target_quantity,
            unit=request.unit, is_active=request.is_active,
            created_at=now, updated_at=now,
        )
        return self.repository.create_need(need, user.user_id, user.role)

    def list_organization_needs(self, user: UserContext, organization_id: str) -> list[DonationNeed]:
        self._authorize_organization_staff(user, organization_id)
        return self.repository.list_needs_for_organization(organization_id)

    def update_need(self, user: UserContext, organization_id: str, need_id: str, request: DonationNeedUpdateRequest) -> DonationNeed:
        self._authorize_organization_staff(user, organization_id)
        existing = self.repository.get_need_for_organization(organization_id, need_id)
        if existing is None:
            raise LookupError("Donation need not found for this organization")
        changes = request.model_dump(exclude_unset=True)
        for field in ("title", "category", "need_type", "is_active"):
            if field in changes and changes[field] is None:
                raise ValueError(f"{field} cannot be null")
        merged = {
            "title": existing.title, "description": existing.description,
            "category": existing.category, "need_type": existing.need_type,
            "target_amount": existing.target_amount,
            "target_quantity": existing.target_quantity, "unit": existing.unit,
            "is_active": existing.is_active,
        }
        merged.update(changes)
        try:
            validated = DonationNeedCreateRequest(**merged)
        except ValidationError as exc:
            raise ValueError(str(exc)) from exc
        changes.update({
            "need_type": validated.need_type,
            "target_amount": validated.target_amount,
            "target_quantity": validated.target_quantity,
            "unit": validated.unit,
        })
        updated = self.repository.update_need(organization_id, need_id, changes, user.user_id, user.role)
        if updated is None:
            raise LookupError("Donation need not found for this organization")
        return updated

    def list_public_needs(self, organization_id: str | None = None) -> list[DonationNeed]:
        return self.repository.list_public_needs(organization_id)

    def get_public_need(self, need_id: str) -> DonationNeed:
        need = self.repository.get_public_need(need_id)
        if need is None:
            raise LookupError("Active donation need not found")
        return need
