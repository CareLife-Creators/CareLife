from datetime import datetime, timezone
from uuid import uuid4

from app.application.interfaces.child import ChildRepository
from app.application.schemas.child import (
    ChildCreateRequest,
    ChildUpdateRequest,
    OutcomeCreateRequest,
    OutcomeUpdateRequest,
)
from app.domain.entities.child import Child, OrphanageOutcome
from app.domain.entities.user_context import Role, UserContext


class ChildService:
    def __init__(self, repository: ChildRepository):
        self.repository = repository

    @staticmethod
    def _organization_access(
        user: UserContext,
        organization_id: str,
    ) -> bool:
        return (
            organization_id in user.organization_ids
            or user.organization_id == organization_id
        )

    def _check_orphanage_staff(
        self,
        user: UserContext,
        organization_id: str,
    ) -> None:
        if user.role != Role.ORPHANAGE_STAFF:
            raise PermissionError("Orphanage staff access required")

        if not self._organization_access(user, organization_id):
            raise PermissionError(
                "You do not have access to this organization"
            )

        if not self.repository.organization_is_orphanage(
            organization_id
        ):
            raise ValueError("Organization is not an orphanage")

    def authorize_child_access(
        self,
        user: UserContext,
        child: Child,
    ) -> None:
        """Allow only authorized users to access a private child record."""
        if user.role == Role.CARELIFE_ADMIN:
            return

        if user.role != Role.ORPHANAGE_STAFF:
            raise PermissionError(
                "Orphanage staff access required"
            )

        organization_id = child.orphanage_organization_id

        if organization_id is None:
            raise PermissionError(
                "Child is not assigned to an orphanage"
            )

        if not self._organization_access(user, organization_id):
            raise PermissionError(
                "You do not have access to this child record"
            )

    def authorize_outcome_access(
        self,
        user: UserContext,
        outcome: OrphanageOutcome,
    ) -> None:
        """Use the child record as the source of truth for outcome access."""
        child = self.repository.get(outcome.child_id)

        if child is None:
            raise ValueError("Child record not found")

        self.authorize_child_access(user, child)

        if child.orphanage_organization_id != outcome.organization_id:
            raise PermissionError(
                "Outcome does not belong to this child organization"
            )

    def create(
        self,
        user: UserContext,
        organization_id: str,
        request: ChildCreateRequest,
    ) -> Child:
        self._check_orphanage_staff(user, organization_id)

        now = datetime.now(timezone.utc)

        child = Child(
            id=str(uuid4()),
            parent_id=None,
            full_name=request.full_name,
            date_of_birth=request.date_of_birth,
            gender=request.gender,
            allergies=request.allergies,
            medical_notes=request.medical_notes,
            orphanage_organization_id=organization_id,
            daycare_organization_id=None,
            created_at=now,
            updated_at=now,
        )

        return self.repository.create(child)

    def list_children(
        self,
        user: UserContext,
        organization_id: str,
    ) -> list[Child]:
        self._check_orphanage_staff(user, organization_id)
        return self.repository.list_by_orphanage(organization_id)

    def get(
        self,
        user: UserContext,
        child_id: str,
    ) -> Child:
        child = self.repository.get(child_id)

        if child is None:
            raise ValueError("Child record not found")

        self.authorize_child_access(user, child)
        return child

    def update(
        self,
        user: UserContext,
        child_id: str,
        request: ChildUpdateRequest,
    ) -> Child:
        child = self.get(user, child_id)

        if request.full_name is not None:
            child.full_name = request.full_name
        if request.gender is not None:
            child.gender = request.gender
        if request.allergies is not None:
            child.allergies = request.allergies
        if request.medical_notes is not None:
            child.medical_notes = request.medical_notes

        child.updated_at = datetime.now(timezone.utc)

        updated = self.repository.update(child)
        if updated is None:
            raise ValueError("Child record not found")

        return updated

    def delete(
        self,
        user: UserContext,
        child_id: str,
    ) -> None:
        child = self.get(user, child_id)

        if child.orphanage_organization_id is None:
            raise ValueError("Child is not assigned to an orphanage")

        if not self.repository.delete(child_id):
            raise ValueError("Child record not found")

    def create_outcome(
        self,
        user: UserContext,
        child_id: str,
        request: OutcomeCreateRequest,
    ) -> OrphanageOutcome:
        child = self.get(user, child_id)

        if child.orphanage_organization_id is None:
            raise ValueError("Child is not assigned to an orphanage")

        now = datetime.now(timezone.utc)

        outcome = OrphanageOutcome(
            id=str(uuid4()),
            child_id=child.id,
            organization_id=child.orphanage_organization_id,
            outcome_type=request.outcome_type,
            outcome_status=request.outcome_status,
            outcome_date=request.outcome_date,
            notes=request.notes,
            created_by=user.user_id,
            created_at=now,
            updated_at=now,
        )

        return self.repository.create_outcome(outcome)

    def list_outcomes(
        self,
        user: UserContext,
        child_id: str,
    ) -> list[OrphanageOutcome]:
        self.get(user, child_id)
        return self.repository.list_outcomes(child_id)

    def get_outcome(
        self,
        user: UserContext,
        outcome_id: str,
    ) -> OrphanageOutcome:
        outcome = self.repository.get_outcome(outcome_id)

        if outcome is None:
            raise ValueError("Outcome record not found")

        self.authorize_outcome_access(user, outcome)
        return outcome

    def update_outcome(
        self,
        user: UserContext,
        outcome_id: str,
        request: OutcomeUpdateRequest,
    ) -> OrphanageOutcome:
        outcome = self.get_outcome(user, outcome_id)

        outcome.outcome_status = request.outcome_status
        outcome.outcome_date = request.outcome_date
        outcome.notes = request.notes
        outcome.updated_at = datetime.now(timezone.utc)

        updated = self.repository.update_outcome(outcome)
        if updated is None:
            raise ValueError("Outcome record not found")

        return updated

    def delete_outcome(
        self,
        user: UserContext,
        outcome_id: str,
    ) -> None:
        self.get_outcome(user, outcome_id)

        if not self.repository.delete_outcome(outcome_id):
            raise ValueError("Outcome record not found")