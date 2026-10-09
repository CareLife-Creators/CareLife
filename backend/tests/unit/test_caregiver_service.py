
import unittest
from datetime import datetime, timezone
from unittest.mock import Mock

from app.application.schemas.caregiver import (
    CaregiverProfileCreateRequest,
    CaregiverVerificationDecisionRequest,
)
from app.application.use_cases.caregivers import CaregiverService
from app.domain.entities.caregiver import (
    CaregiverDocument,
    CaregiverDocumentType,
    CaregiverProfile,
    CaregiverType,
    CaregiverVerificationStatus,
)
from app.domain.entities.user_context import Role, UserContext


class CaregiverServiceTests(unittest.TestCase):

    def setUp(self):
        self.repository = Mock()
        self.service = CaregiverService(self.repository)

        self.caregiver = UserContext(
            user_id="caregiver-1",
            role=Role.INDEPENDENT_CAREGIVER,
        )

        self.admin = UserContext(
            user_id="admin-1",
            role=Role.CARELIFE_ADMIN,
        )

    def make_profile(self, documents=None, status=None):
        now = datetime.now(timezone.utc)

        return CaregiverProfile(
            user_id="caregiver-1",
            full_name="Caregiver Test",
            phone=None,
            service_type=CaregiverType.NANNY,
            bio="Experienced caregiver",
            experience_years=3,
            location="Dhaka",
            verification_status=(
                status or CaregiverVerificationStatus.PENDING
            ),
            review_message=None,
            reviewed_at=None,
            created_at=now,
            updated_at=now,
            documents=documents or [],
        )

    def test_caregiver_can_create_profile(self):
        request = CaregiverProfileCreateRequest(
            service_type=CaregiverType.NANNY,
            experience_years=3,
            location="Dhaka",
        )

        self.repository.get_profile.return_value = None
        self.repository.create_profile.return_value = self.make_profile()

        profile = self.service.create_profile(
            self.caregiver,
            request,
        )

        self.assertEqual(profile.user_id, "caregiver-1")
        self.assertEqual(
            profile.verification_status,
            CaregiverVerificationStatus.PENDING,
        )
        self.repository.create_profile.assert_called_once()

    def test_non_caregiver_cannot_create_profile(self):
        parent = UserContext(
            user_id="parent-1",
            role=Role.PARENT_GUARDIAN,
        )

        request = CaregiverProfileCreateRequest(
            service_type=CaregiverType.NANNY,
        )

        with self.assertRaises(PermissionError):
            self.service.create_profile(parent, request)

        self.repository.create_profile.assert_not_called()

    def test_cannot_create_duplicate_profile(self):
        self.repository.get_profile.return_value = self.make_profile()

        request = CaregiverProfileCreateRequest(
            service_type=CaregiverType.NANNY,
        )

        with self.assertRaises(ValueError):
            self.service.create_profile(self.caregiver, request)

        self.repository.create_profile.assert_not_called()

    def test_approval_requires_both_document_types(self):
        identity_document = CaregiverDocument(
            id="doc-1",
            document_type=CaregiverDocumentType.IDENTITY,
            document_reference="private/identity.pdf",
            submitted_at=datetime.now(timezone.utc),
        )

        self.repository.get_profile.return_value = self.make_profile(
            documents=[identity_document]
        )

        request = CaregiverVerificationDecisionRequest(
            status="approved",
        )

        with self.assertRaises(ValueError):
            self.service.review_profile(
                self.admin,
                "caregiver-1",
                request,
            )

        self.repository.review_profile.assert_not_called()

    def test_approval_succeeds_when_required_documents_exist(self):
        now = datetime.now(timezone.utc)

        documents = [
            CaregiverDocument(
                id="doc-1",
                document_type=CaregiverDocumentType.IDENTITY,
                document_reference="private/identity.pdf",
                submitted_at=now,
            ),
            CaregiverDocument(
                id="doc-2",
                document_type=CaregiverDocumentType.QUALIFICATION,
                document_reference="private/qualification.pdf",
                submitted_at=now,
            ),
        ]

        pending = self.make_profile(documents=documents)
        approved = self.make_profile(
            documents=documents,
            status=CaregiverVerificationStatus.APPROVED,
        )

        self.repository.get_profile.return_value = pending
        self.repository.review_profile.return_value = approved

        result = self.service.review_profile(
            self.admin,
            "caregiver-1",
            CaregiverVerificationDecisionRequest(
                status="approved",
                message="Documents reviewed",
            ),
        )

        self.assertEqual(
            result.verification_status,
            CaregiverVerificationStatus.APPROVED,
        )

        self.repository.review_profile.assert_called_once()


if __name__ == "__main__":
    unittest.main()