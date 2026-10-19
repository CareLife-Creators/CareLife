from app.application.interfaces.role_request import RoleRequestRepository
from app.domain.entities.role_request import RoleRequest


STAFF_ROLES = frozenset({
    "daycare_staff",
    "orphanage_staff",
    "care_home_staff",
})
ROLE_REQUEST_STATUSES = frozenset({
    "pending",
    "approved",
    "rejected",
})


class RoleRequestService:
    def __init__(self, repository: RoleRequestRepository):
        self.repository = repository

    def create(
        self,
        user_id: str,
        requested_role: str,
        note: str | None = None,
    ) -> RoleRequest:
        if requested_role not in STAFF_ROLES:
            raise ValueError("Invalid staff role requested")
        return self.repository.create(
            user_id=user_id,
            requested_role=requested_role,
            note=(note.strip() or None) if note else None,
        )

    def list_for_user(self, user_id: str) -> list[RoleRequest]:
        return self.repository.list_for_user(user_id)

    def list_by_status(self, status: str = "pending") -> list[RoleRequest]:
        if status not in ROLE_REQUEST_STATUSES:
            raise ValueError("Invalid role request status")
        return self.repository.list_by_status(status)

    def approve(
        self,
        request_id: str,
        reviewer_id: str,
        reviewer_role: str,
    ) -> RoleRequest | None:
        if reviewer_role != "carelife_admin":
            raise PermissionError("Only carelife_admin can approve role requests")
        return self.repository.approve(
            request_id,
            reviewer_id,
            reviewer_role,
        )

    def reject(
        self,
        request_id: str,
        reviewer_id: str,
        reviewer_role: str,
    ) -> RoleRequest | None:
        if reviewer_role != "carelife_admin":
            raise PermissionError("Only carelife_admin can reject role requests")
        return self.repository.reject(
            request_id,
            reviewer_id,
            reviewer_role,
        )
