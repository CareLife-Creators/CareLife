from typing import Protocol

from app.domain.entities.role_request import RoleRequest


class RoleRequestRepository(Protocol):
    def create(
        self,
        user_id: str,
        requested_role: str,
        note: str | None,
    ) -> RoleRequest:
        ...

    def list_for_user(self, user_id: str) -> list[RoleRequest]:
        ...

    def list_by_status(self, status: str) -> list[RoleRequest]:
        ...

    def approve(
        self,
        request_id: str,
        reviewer_id: str,
        reviewer_role: str,
    ) -> RoleRequest | None:
        ...

    def reject(
        self,
        request_id: str,
        reviewer_id: str,
        reviewer_role: str,
    ) -> RoleRequest | None:
        ...
