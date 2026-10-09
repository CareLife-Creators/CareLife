from datetime import datetime
from typing import Protocol

from app.domain.entities.child import (
    Attendance,
    Child,
    ChildContact,
    DailyUpdate,
    OrphanageOutcome,
)


class ChildRepository(Protocol):
    def organization_is_orphanage(
        self,
        organization_id: str,
    ) -> bool:
        ...

    def create(self, child: Child) -> Child:
        ...

    def list_by_orphanage(
        self,
        organization_id: str,
    ) -> list[Child]:
        ...

    def list_by_parent(
        self,
        parent_id: str,
    ) -> list[Child]:
        ...

    def get(self, child_id: str) -> Child | None:
        ...

    def update(self, child: Child) -> Child | None:
        ...

    def delete(self, child_id: str) -> bool:
        ...

    def create_outcome(
        self,
        outcome: OrphanageOutcome,
    ) -> OrphanageOutcome:
        ...

    def list_outcomes(
        self,
        child_id: str,
    ) -> list[OrphanageOutcome]:
        ...

    def get_outcome(
        self,
        outcome_id: str,
    ) -> OrphanageOutcome | None:
        ...

    def update_outcome(
        self,
        outcome: OrphanageOutcome,
    ) -> OrphanageOutcome | None:
        ...

    def delete_outcome(
        self,
        outcome_id: str,
    ) -> bool:
        ...

    def create_contact(
        self,
        contact: ChildContact,
    ) -> ChildContact:
        ...

    def list_contacts(
        self,
        child_id: str,
        contact_type: str,
    ) -> list[ChildContact]:
        ...


class AttendanceRepository(Protocol):
    def create_check_in(
        self,
        attendance: Attendance,
    ) -> Attendance:
        ...

    def get_by_id(
        self,
        attendance_id: str,
    ) -> Attendance | None:
        ...

    def check_out(
        self,
        attendance_id: str,
        when: datetime,
    ) -> Attendance | None:
        ...

    def list_for_child(
        self,
        child_id: str,
        daycare_organization_id: str | None = None,
    ) -> list[Attendance]:
        ...

    def has_approved_enrollment(
        self,
        child_id: str,
        daycare_organization_id: str,
    ) -> bool:
        ...

    def create_daily_update(
        self,
        update: DailyUpdate,
    ) -> DailyUpdate:
        ...

    def list_daily_updates(
        self,
        child_id: str,
        daycare_organization_id: str | None = None,
    ) -> list[DailyUpdate]:
        ...