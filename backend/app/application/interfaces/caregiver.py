
from typing import Protocol

from app.domain.entities.caregiver import (
    CaregiverProfile,
    CaregiverPublicProfile,
    CaregiverType,
    CaregiverVerificationStatus,
)


class CaregiverRepository(Protocol):

    def create_profile(
        self,
        user_id: str,
        service_type: CaregiverType,
        bio: str | None,
        experience_years: int,
        location: str | None,
    ) -> CaregiverProfile:
        ...

    def get_profile(
        self,
        user_id: str,
    ) -> CaregiverProfile | None:
        ...

    def update_profile(
        self,
        user_id: str,
        updates: dict[str, object],
    ) -> CaregiverProfile | None:
        ...

    def submit_document(
        self,
        user_id: str,
        document_type: str,
        document_reference: str,
    ) -> CaregiverProfile | None:
        ...

    def list_pending_profiles(
        self,
    ) -> list[CaregiverProfile]:
        ...

    def review_profile(
        self,
        caregiver_id: str,
        status: CaregiverVerificationStatus,
        reviewer_id: str,
        message: str | None,
    ) -> CaregiverProfile | None:
        ...

    def list_public_profiles(
        self,
        search: str | None = None,
        location: str | None = None,
        service_type: CaregiverType | None = None,
    ) -> list[CaregiverPublicProfile]:
        ...

    def get_public_profile(
        self,
        caregiver_id: str,
    ) -> CaregiverPublicProfile | None:
        ...