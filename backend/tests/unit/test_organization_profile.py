import unittest
from datetime import datetime, timezone

from pydantic import ValidationError

from app.application.schemas.organization_profile import (
    OrganizationProfileUpdateRequest,
)
from app.application.use_cases.organization_profile import (
    OrganizationProfileService,
)
from app.domain.entities.organization import OrganizationStatus
from app.domain.entities.organization_profile import (
    OrganizationProfile,
)


def make_profile(
    organization_type: str = "daycare",
    status: OrganizationStatus = OrganizationStatus.VERIFIED,
) -> OrganizationProfile:
    return OrganizationProfile(
        organization_id="org-1",
        organization_name="Sunshine Daycare",
        organization_type=organization_type,
        description="A childcare center",
        location="Dhaka",
        contact="+8801712345678",
        capacity=20,
        age_range="6 months–5 years",
        opening_hours="8:00 AM–6:00 PM",
        facilities="CCTV, playground",
        fees="BDT 6,000 per month",
        status=status,
        updated_at=datetime.now(timezone.utc),
    )


class FakeOrganizationProfileRepository:

    def __init__(self, profile: OrganizationProfile):
        self.profile = profile

    def get_for_staff(self, organization_id):
        if organization_id != self.profile.organization_id:
            return None
        return self.profile

    def get_public(self, organization_id):
        profile = self.get_for_staff(organization_id)

        if (
            profile is None
            or profile.status != OrganizationStatus.VERIFIED
        ):
            return None

        return profile

    def update_profile(
        self,
        organization_id,
        changes,
        updated_by,
    ):
        if self.get_for_staff(organization_id) is None:
            return None

        self.profile = self.profile.model_copy(
            update={
                **changes,
                "updated_at": datetime.now(timezone.utc),
            }
        )

        return self.profile


class OrganizationProfileServiceTests(unittest.TestCase):

    def setUp(self):
        self.repository = FakeOrganizationProfileRepository(
            make_profile()
        )
        self.service = OrganizationProfileService(
            self.repository
        )

    def test_staff_can_view_matching_organization_profile(self):
        profile = self.service.get_staff_profile(
            "org-1",
            "daycare",
        )

        self.assertEqual(
            profile.organization_name,
            "Sunshine Daycare",
        )

    def test_missing_profile_is_rejected(self):
        with self.assertRaises(LookupError):
            self.service.get_staff_profile(
                "missing-org",
                "daycare",
            )

    def test_wrong_organization_type_is_rejected(self):
        with self.assertRaises(PermissionError):
            self.service.get_staff_profile(
                "org-1",
                "orphanage",
            )

    def test_staff_can_update_daycare_service_information(self):
        profile = self.service.update_profile(
            organization_id="org-1",
            changes={
                "capacity": 35,
                "facilities": "CCTV, playground, meals",
            },
            updated_by="staff-1",
            expected_organization_type="daycare",
        )

        self.assertEqual(profile.capacity, 35)
        self.assertEqual(
            profile.facilities,
            "CCTV, playground, meals",
        )

    def test_non_daycare_cannot_update_daycare_fields(self):
        self.repository = FakeOrganizationProfileRepository(
            make_profile(organization_type="orphanage")
        )
        self.service = OrganizationProfileService(
            self.repository
        )

        with self.assertRaises(ValueError):
            self.service.update_profile(
                organization_id="org-1",
                changes={"capacity": 40},
                updated_by="staff-1",
                expected_organization_type="orphanage",
            )

    def test_public_profile_is_not_available_when_pending(self):
        self.repository = FakeOrganizationProfileRepository(
            make_profile(status=OrganizationStatus.PENDING)
        )
        self.service = OrganizationProfileService(
            self.repository
        )

        with self.assertRaises(LookupError):
            self.service.get_public_profile("org-1")


class OrganizationProfileSchemaTests(unittest.TestCase):

    def test_update_text_is_normalized(self):
        request = OrganizationProfileUpdateRequest(
            organization_name="  Sunshine Daycare  ",
            facilities=" CCTV, playground ",
        )

        self.assertEqual(
            request.organization_name,
            "Sunshine Daycare",
        )
        self.assertEqual(
            request.facilities,
            "CCTV, playground",
        )

    def test_empty_update_is_rejected(self):
        with self.assertRaises(ValidationError):
            OrganizationProfileUpdateRequest()

    def test_negative_capacity_is_rejected(self):
        with self.assertRaises(ValidationError):
            OrganizationProfileUpdateRequest(
                capacity=-1
            )

    def test_unapproved_request_field_is_rejected(self):
        with self.assertRaises(ValidationError):
            OrganizationProfileUpdateRequest(
                status="verified"
            )


if __name__ == "__main__":
    unittest.main()