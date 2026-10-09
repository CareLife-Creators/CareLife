
from app.application.interfaces.caregiver import CaregiverRepository
from app.application.schemas.caregiver import (
    CaregiverDocumentSubmitRequest,
    CaregiverProfileCreateRequest,
    CaregiverProfileUpdateRequest,
    CaregiverVerificationDecisionRequest,
)
from app.domain.entities.caregiver import (
    CaregiverDocumentType,
    CaregiverProfile,
    CaregiverPublicProfile,
    CaregiverType,
    CaregiverVerificationStatus,
)
from app.domain.entities.user_context import Role, UserContext


class CaregiverService:

    def __init__(self, repository: CaregiverRepository):
        self.repository = repository

    @staticmethod
    def _require_caregiver(user: UserContext) -> None:
        if user.role != Role.INDEPENDENT_CAREGIVER:
            raise PermissionError(
                "Independent caregiver access required"
            )

    @staticmethod
    def _require_admin(user: UserContext) -> None:
        if user.role != Role.CARELIFE_ADMIN:
            raise PermissionError(
                "CareLife administrator access required"
            )

    def create_profile(
        self,
        user: UserContext,
        request: CaregiverProfileCreateRequest,
    ) -> CaregiverProfile:
        self._require_caregiver(user)

        if self.repository.get_profile(user.user_id) is not None:
            raise ValueError(
                "Caregiver profile already exists"
            )

        return self.repository.create_profile(
            user_id=user.user_id,
            service_type=request.service_type,
            bio=request.bio,
            experience_years=request.experience_years,
            location=request.location,
        )

    def get_my_profile(
        self,
        user: UserContext,
    ) -> CaregiverProfile:
        self._require_caregiver(user)

        profile = self.repository.get_profile(user.user_id)

        if profile is None:
            raise LookupError("Caregiver profile not found")

        return profile

    def update_profile(
        self,
        user: UserContext,
        request: CaregiverProfileUpdateRequest,
    ) -> CaregiverProfile:
        self._require_caregiver(user)

        updates = request.model_dump(exclude_unset=True)

        if not updates:
            raise ValueError(
                "Provide at least one field to update"
            )

        if (
            "service_type" in updates
            and updates["service_type"] is None
        ):
            raise ValueError(
                "Service type cannot be empty"
            )

        if (
            "experience_years" in updates
            and updates["experience_years"] is None
        ):
            raise ValueError(
                "Experience years cannot be empty"
            )

        if self.repository.get_profile(user.user_id) is None:
            raise LookupError("Caregiver profile not found")

        updated = self.repository.update_profile(
            user.user_id,
            updates,
        )

        if updated is None:
            raise LookupError("Caregiver profile not found")

        return updated

    def submit_document(
        self,
        user: UserContext,
        request: CaregiverDocumentSubmitRequest,
    ) -> CaregiverProfile:
        self._require_caregiver(user)

        if self.repository.get_profile(user.user_id) is None:
            raise LookupError(
                "Create your caregiver profile before submitting documents"
            )

        profile = self.repository.submit_document(
            user.user_id,
            request.document_type,
            request.document_reference,
        )

        if profile is None:
            raise LookupError("Caregiver profile not found")

        return profile

    def list_pending_profiles(
        self,
        user: UserContext,
    ) -> list[CaregiverProfile]:
        self._require_admin(user)

        return self.repository.list_pending_profiles()

    def review_profile(
        self,
        user: UserContext,
        caregiver_id: str,
        request: CaregiverVerificationDecisionRequest,
    ) -> CaregiverProfile:
        self._require_admin(user)

        profile = self.repository.get_profile(caregiver_id)

        if profile is None:
            raise LookupError("Caregiver profile not found")

        if profile.verification_status != CaregiverVerificationStatus.PENDING:
            raise ValueError(
                "Only pending caregiver profiles can be reviewed"
            )

        requested_status = CaregiverVerificationStatus(request.status)

        if requested_status == CaregiverVerificationStatus.APPROVED:
            submitted_types = {
                document.document_type
                for document in profile.documents
            }

            required_types = {
                CaregiverDocumentType.IDENTITY,
                CaregiverDocumentType.QUALIFICATION,
            }

            if not required_types.issubset(submitted_types):
                raise ValueError(
                    "Identity and qualification documents are required "
                    "before approval"
                )

        updated = self.repository.review_profile(
            caregiver_id=caregiver_id,
            status=requested_status,
            reviewer_id=user.user_id,
            message=request.message,
        )

        if updated is None:
            raise ValueError(
                "The caregiver profile is no longer pending review"
            )

        return updated

    def list_public_profiles(
        self,
        search: str | None = None,
        location: str | None = None,
        service_type: CaregiverType | None = None,
    ) -> list[CaregiverPublicProfile]:
        return self.repository.list_public_profiles(
            search=search,
            location=location,
            service_type=service_type,
        )

    def get_public_profile(
        self,
        caregiver_id: str,
    ) -> CaregiverPublicProfile:
        profile = self.repository.get_public_profile(caregiver_id)

        if profile is None:
            raise LookupError("Approved caregiver not found")

        return profile