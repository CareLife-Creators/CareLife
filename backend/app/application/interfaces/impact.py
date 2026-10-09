from typing import Protocol

from app.domain.entities.impact import ImpactMedia, ImpactUpdate


class ImpactRepository(Protocol):
    def is_authorized_orphanage_staff(
        self,
        organization_id: str,
        user_id: str,
    ) -> bool:
        ...

    def create_update(self, update: ImpactUpdate) -> ImpactUpdate:
        ...

    def get_update(self, update_id: str) -> ImpactUpdate | None:
        ...

    def list_public_updates(
        self,
        organization_id: str | None = None,
    ) -> list[ImpactUpdate]:
        ...

    def list_pending_updates(self) -> list[ImpactUpdate]:
        ...

    def add_media(
        self,
        organization_id: str,
        user_id: str,
        media: ImpactMedia,
    ) -> ImpactMedia:
        ...

    def list_media(self, update_id: str) -> list[ImpactMedia]:
        ...

    def get_media(self, media_id: str) -> ImpactMedia | None:
        ...

    def review_update(
        self,
        update_id: str,
        decision: str,
        reviewer_id: str,
        review_notes: str | None,
    ) -> ImpactUpdate | None:
        ...

    def get_public_media(self, media_id: str) -> ImpactMedia | None:
        ...
