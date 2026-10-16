from app.application.interfaces.organization_profile import (
    OrganizationProfileRepository,
)
from app.domain.entities.organization_profile import (
    OrganizationProfile,
)


EDITABLE_FIELDS = {
    "organization_name",
    "description",
    "location",
    "contact",
    "capacity",
    "age_range",
    "opening_hours",
    "facilities",
    "fees",
}

DAYCARE_FIELDS = {
    "capacity",
    "age_range",
    "opening_hours",
    "facilities",
    "fees",
}


class OrganizationProfileService:

    def __init__(
        self,
        repository: OrganizationProfileRepository,
    ):
        self.repository = repository

    def get_staff_profile(
        self,
        organization_id: str,
        expected_organization_type: str,
    ) -> OrganizationProfile:
        profile = self.repository.get_for_staff(
            organization_id
        )

        if profile is None:
            raise LookupError(
                "Organization profile not found."
            )

        self._ensure_correct_organization_type(
            profile,
            expected_organization_type,
        )

        return profile

    def update_profile(
        self,
        organization_id: str,
        changes: dict[str, object],
        updated_by: str,
        expected_organization_type: str,
    ) -> OrganizationProfile:

        if not changes:
            raise ValueError(
                "At least one organization field must be provided."
            )

        unsupported_fields = (
            set(changes) - EDITABLE_FIELDS
        )

        if unsupported_fields:
            raise ValueError(
                "The request contains fields that cannot be updated."
            )

        profile = self.repository.get_for_staff(
            organization_id
        )

        if profile is None:
            raise LookupError(
                "Organization profile not found."
            )

        self._ensure_correct_organization_type(
            profile,
            expected_organization_type,
        )

        if (
            profile.organization_type != "daycare"
            and set(changes).intersection(DAYCARE_FIELDS)
        ):
            raise ValueError(
                "Daycare service fields can only be updated "
                "for daycare organizations."
            )

        if "organization_name" in changes:
            name = changes["organization_name"]

            if not isinstance(name, str) or not name.strip():
                raise ValueError(
                    "Organization name cannot be empty."
                )

        if "capacity" in changes:
            capacity = changes["capacity"]

            if (
                not isinstance(capacity, int)
                or isinstance(capacity, bool)
                or capacity < 0
            ):
                raise ValueError(
                    "Capacity must be a non-negative integer."
                )

        updated_profile = self.repository.update_profile(
            organization_id=organization_id,
            changes=changes,
            updated_by=updated_by,
        )

        if updated_profile is None:
            raise LookupError(
                "Organization profile not found."
            )

        return updated_profile

    def get_public_profile(
        self,
        organization_id: str,
    ) -> OrganizationProfile:
        profile = self.repository.get_public(
            organization_id
        )

        if profile is None:
            raise LookupError(
                "Public organization profile not found."
            )

        return profile

    @staticmethod
    def _ensure_correct_organization_type(
        profile: OrganizationProfile,
        expected_organization_type: str,
    ) -> None:
        if (
            profile.organization_type
            != expected_organization_type
        ):
            raise PermissionError(
                "Your staff role cannot manage this "
                "organization type."
            )