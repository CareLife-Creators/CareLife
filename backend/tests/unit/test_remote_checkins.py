from unittest.mock import MagicMock, Mock

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
from app.infrastructure.repositories.remote_checkins import (
    PostgresRemoteCheckInRepository,
)


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


def make_connection_context():
    context = MagicMock()
    connection = context.__enter__.return_value
    connection.transaction.return_value.__enter__.return_value = None
    return context, connection


def test_repository_rejects_checkin_without_active_consent(monkeypatch):
    context, connection = make_connection_context()
    connection.execute.return_value.fetchone.return_value = None
    monkeypatch.setattr(
        "app.infrastructure.repositories.remote_checkins.get_connection",
        lambda: context,
    )

    repository = PostgresRemoteCheckInRepository()

    with pytest.raises(PermissionError, match="Active consent"):
        repository.create_checkin(
            actor_user_id="family-1",
            resident_id="resident-1",
            wellbeing_status="well",
            notes=None,
        )

    connection.execute.assert_called_once()


def test_family_history_requires_active_consent(monkeypatch):
    context, connection = make_connection_context()
    connection.execute.return_value.fetchone.return_value = None
    monkeypatch.setattr(
        "app.infrastructure.repositories.remote_checkins.get_connection",
        lambda: context,
    )

    repository = PostgresRemoteCheckInRepository()

    with pytest.raises(PermissionError, match="Active consent"):
        repository.list_checkins(
            user=make_user(
                Role.FAMILY_REPRESENTATIVE,
                "family-1",
            ),
            resident_id="resident-1",
        )

    connection.execute.assert_called_once()


def test_care_home_history_query_is_scoped_to_member_organizations(
    monkeypatch,
):
    context, connection = make_connection_context()
    connection.execute.side_effect = [
        Mock(fetchone=Mock(return_value=(1,))),
        Mock(fetchall=Mock(return_value=[])),
    ]
    monkeypatch.setattr(
        "app.infrastructure.repositories.remote_checkins.get_connection",
        lambda: context,
    )

    repository = PostgresRemoteCheckInRepository()
    repository.list_checkins(
        user=make_user(Role.CARE_HOME_STAFF, "staff-1"),
        resident_id="resident-1",
    )

    history_query, parameters = connection.execute.call_args_list[1].args
    assert "organization_id IN" in history_query
    assert "user_organizations" in history_query
    assert parameters == (
        "resident-1",
        "resident-1",
        "staff-1",
    )
