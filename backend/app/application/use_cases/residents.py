from datetime import date

from app.application.interfaces.resident import (
    ResidentProfileRepository,
)
from app.application.schemas.resident import (
    ResidentProfileCreateRequest,
)
from app.domain.entities.resident import (
    ResidentProfile,
    ResidentProfileStatus,
)
from app.domain.entities.user_context import Role, UserContext


EDITABLE_FIELDS = {
    "full_name",
    "preferred_name",
    "date_of_birth",
    "room_number",
    "emergency_contact_name",
    "emergency_contact_phone",
    "status",
}


class ResidentProfileService:

    def __init__(
        self,
        repository: ResidentProfileRepository,
    ):
        self.repository = repository

    @staticmethod
    def _require_authorized_staff(
        user: UserContext,
    ) -> None:
        if user.role not in {
            Role.CARE_HOME_STAFF,
            Role.CARELIFE_ADMIN,
        }:
            raise PermissionError(
                "Only authorized care-home staff or administrators "
                "can manage resident profiles"
            )

    def create_profile(
        self,
        user: UserContext,
        organization_id: str,
        request: ResidentProfileCreateRequest,
    ) -> ResidentProfile:
        self._require_authorized_staff(user)

        return self.repository.create_profile(
            user=user,
            organization_id=organization_id,
            values=request.model_dump(),
        )

    def list_profiles(
        self,
        user: UserContext,
        organization_id: str,
        profile_status: ResidentProfileStatus | None = None,
    ) -> list[ResidentProfile]:
        self._require_authorized_staff(user)

        return self.repository.list_profiles(
            user=user,
            organization_id=organization_id,
            profile_status=profile_status,
        )

    def get_profile(
        self,
        user: UserContext,
        organization_id: str,
        resident_id: str,
    ) -> ResidentProfile:
        self._require_authorized_staff(user)

        profile = self.repository.get_profile(
            user=user,
            organization_id=organization_id,
            resident_id=resident_id,
        )

        if profile is None:
            raise LookupError("Resident profile not found")

        return profile

    def update_profile(
        self,
        user: UserContext,
        organization_id: str,
        resident_id: str,
        changes: dict[str, object],
    ) -> ResidentProfile:
        self._require_authorized_staff(user)

        if not changes:
            raise ValueError(
                "At least one resident field must be provided"
            )

        unsupported_fields = set(changes) - EDITABLE_FIELDS

        if unsupported_fields:
            raise ValueError(
                "The request contains fields that cannot be updated"
            )

        normalized_changes = dict(changes)

        if "full_name" in normalized_changes:
            name = normalized_changes["full_name"]

            if not isinstance(name, str) or not name.strip():
                raise ValueError(
                    "Resident name cannot be empty"
                )

            normalized_changes["full_name"] = name.strip()

        if (
            "status" in normalized_changes
            and normalized_changes["status"] is None
        ):
            raise ValueError("Resident status cannot be null")

        if "date_of_birth" in normalized_changes:
            birth_date = normalized_changes["date_of_birth"]

            if (
                birth_date is not None
                and (
                    not isinstance(birth_date, date)
                    or birth_date > date.today()
                )
            ):
                raise ValueError(
                    "Date of birth cannot be in the future"
                )

        for field in (
            "preferred_name",
            "room_number",
            "emergency_contact_name",
        ):
            if field in normalized_changes:
                value = normalized_changes[field]

                if value is not None:
                    if not isinstance(value, str):
                        raise ValueError(
                            f"{field} must be text"
                        )

                    normalized_changes[field] = value.strip() or None

        if "emergency_contact_phone" in normalized_changes:
            phone = normalized_changes["emergency_contact_phone"]

            if phone is not None:
                if not isinstance(phone, str):
                    raise ValueError(
                        "Emergency contact phone must be text"
                    )

                normalized_changes[
                    "emergency_contact_phone"
                ] = phone.strip() or None

        profile = self.repository.update_profile(
            user=user,
            organization_id=organization_id,
            resident_id=resident_id,
            changes=normalized_changes,
        )

        if profile is None:
            raise LookupError("Resident profile not found")

        return profile