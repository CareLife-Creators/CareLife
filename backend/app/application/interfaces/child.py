from datetime import date
from typing import Protocol

from app.domain.entities.child import Child, OrphanageOutcome


class ChildRepository(Protocol):
    def organization_is_orphanage(self, organization_id: str) -> bool:
        ...

    def create(self, child: Child) -> Child:
        ...

    def list_by_orphanage(self, organization_id: str) -> list[Child]:
        ...

    def get(self, child_id: str) -> Child | None:
        ...

    def update(self, child: Child) -> Child | None:
        ...

    def delete(self, child_id: str) -> bool:
        ...

    def create_outcome(self, outcome: OrphanageOutcome) -> OrphanageOutcome:
        ...

    def list_outcomes(self, child_id: str) -> list[OrphanageOutcome]:
        ...

    def get_outcome(self, outcome_id: str) -> OrphanageOutcome | None:
        ...

    def update_outcome(self, outcome: OrphanageOutcome) -> OrphanageOutcome | None:
        ...

    def delete_outcome(self, outcome_id: str) -> bool:
        ...