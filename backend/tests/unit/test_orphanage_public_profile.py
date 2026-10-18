import unittest
from datetime import datetime, timezone

from app.application.use_cases.organization_profile import (
    OrganizationProfileService,
)
from app.domain.entities.organization import OrganizationStatus
from app.domain.entities.organization_profile import (
    OrganizationProfile,
)


def make_profile(
    organization_type: str = "orphanage",
    status: OrganizationStatus = OrganizationStatus.VERIFIED,
) -> OrganizationProfile:
    return OrganizationProfile(
        organization_id="org-53",
        organization_name="Hope Orphanage",
        organization_type=organization_type,
        description="Support and care for children.",
        location="Dhaka",
        contact="+8801700000000",
        capacity=30,
        age_range=None,
        opening_hours=None,
        facilities=None,
        fees=None,
        status=status,
        updated_at=datetime.now(timezone.utc),
    )


class FakeOrganizationProfileRepository:

    def __init__(
        self,
        profile: OrganizationProfile,
    ):
        self.profile = profile

    def get_public(
        self,
        organization_id: str,
    ) -> OrganizationProfile | None:
        if organization_id != self.profile.organization_id:
            return None

        if self.profile.status != OrganizationStatus.VERIFIED:
            return None

        return self.profile


class OrphanagePublicProfileServiceTests(unittest.TestCase):

    def test_verified_orphanage_profile_is_returned(self):
        repository = FakeOrganizationProfileRepository(
            make_profile()
        )
        service = OrganizationProfileService(repository)

        profile = service.get_public_orphanage_profile(
            "org-53"
        )

        self.assertEqual(
            profile.organization_id,
            "org-53",
        )
        self.assertEqual(
            profile.organization_type,
            "orphanage",
        )
        self.assertEqual(
            profile.status,
            OrganizationStatus.VERIFIED,
        )

    def test_daycare_cannot_use_orphanage_profile_endpoint(self):
        repository = FakeOrganizationProfileRepository(
            make_profile(
                organization_type="daycare"
            )
        )
        service = OrganizationProfileService(repository)

        with self.assertRaises(LookupError):
            service.get_public_orphanage_profile(
                "org-53"
            )

    def test_unverified_orphanage_is_not_public(self):
        repository = FakeOrganizationProfileRepository(
            make_profile(
                status=OrganizationStatus.PENDING
            )
        )
        service = OrganizationProfileService(repository)

        with self.assertRaises(LookupError):
            service.get_public_orphanage_profile(
                "org-53"
            )

    def test_missing_organization_is_not_public(self):
        repository = FakeOrganizationProfileRepository(
            make_profile()
        )
        service = OrganizationProfileService(repository)

        with self.assertRaises(LookupError):
            service.get_public_orphanage_profile(
                "missing-org"
            )


if __name__ == "__main__":
    unittest.main()