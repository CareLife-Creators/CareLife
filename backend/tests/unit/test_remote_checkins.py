from unittest.mock import Mock

import pytest

from app.application.schemas.remote_checkin import (
    ConsentUpdateRequest,
    RemoteCheckInCreateRequest,
)
from app.application.use_cases.remote_checkins import (
    RemoteCheckInService,
)
from app.domain.entities.remote_checkin import WellbeingStatus
from app.domain.entities.user_context import Role, UserContext


def make_user(
    role: Role,
    user_id: str = "user-1",
) -> UserContext:
    return UserContext(
        user_id=user_id,
        role=role,
    )


def test_non_family_representative_cannot_create_checkin():
    repository = Mock()
    service = RemoteCheckInService(repository)

    with pytest.raises(
        PermissionError,
        match="Family representative",
    ):
        service.create_checkin(
            user=make_user(Role.PARENT_GUARDIAN),
            resident_id="resident-1",
            request=RemoteCheckInCreateRequest(
                wellbeing_status=WellbeingStatus.WELL,
            ),
        )

    repository.create_checkin.assert_not_called()


def test_family_representative_submits_checkin():
    repository = Mock()
    service = RemoteCheckInService(repository)

    request = RemoteCheckInCreateRequest(
        wellbeing_status=WellbeingStatus.NEEDS_ATTENTION,
        notes="Please arrange a follow-up visit.",
    )

    service.create_checkin(
        user=make_user(
            Role.FAMILY_REPRESENTATIVE,
            "family-1",
        ),
        resident_id="resident-1",
        request=request,
    )

    repository.create_checkin.assert_called_once_with(
        actor_user_id="family-1",
        resident_id="resident-1",
        wellbeing_status="needs_attention",
        notes="Please arrange a follow-up visit.",
    )


def test_parent_cannot_manage_resident_consent():
    repository = Mock()
    service = RemoteCheckInService(repository)

    with pytest.raises(
        PermissionError,
        match="Care-home staff",
    ):
        service.set_consent(
            user=make_user(Role.PARENT_GUARDIAN),
            organization_id="organization-1",
            resident_id="resident-1",
            request=ConsentUpdateRequest(
                family_representative_id="family-1",
                consent_granted=True,
            ),
        )

    repository.set_consent.assert_not_called()


def test_administrator_can_request_consent_update():
    repository = Mock()
    service = RemoteCheckInService(repository)

    request = ConsentUpdateRequest(
        family_representative_id="family-1",
        consent_granted=True,
    )

    service.set_consent(
        user=make_user(Role.CARELIFE_ADMIN, "admin-1"),
        organization_id="organization-1",
        resident_id="resident-1",
        request=request,
    )

    repository.set_consent.assert_called_once_with(
        user=make_user(Role.CARELIFE_ADMIN, "admin-1"),
        organization_id="organization-1",
        resident_id="resident-1",
        family_representative_id="family-1",
        consent_granted=True,
    )