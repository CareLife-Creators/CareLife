from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from app.application.schemas.impact import (
    ImpactReviewRequest,
    ImpactUpdateCreateRequest,
)
from app.application.use_cases.impact import (
    ImpactService,
    validate_media_payload,
)
from app.domain.entities.impact import (
    ImpactMediaType,
    ImpactReviewDecision,
    ImpactUpdate,
    ImpactUpdateStatus,
)
from app.domain.entities.user_context import Role, UserContext


def make_user(
    role: Role = Role.ORPHANAGE_STAFF,
    organization_id: str | None = "org-1",
) -> UserContext:
    organizations = [organization_id] if organization_id else []
    return UserContext(
        user_id="user-1",
        role=role,
        organization_id=organization_id,
        organization_ids=organizations,
    )


def make_update(
    status: ImpactUpdateStatus = ImpactUpdateStatus.PENDING_REVIEW,
) -> ImpactUpdate:
    now = datetime.now(timezone.utc)
    return ImpactUpdate(
        id="update-1",
        organization_id="org-1",
        organization_name="Example Orphanage",
        title="A safe update",
        content="A suitable update about the organization's work.",
        status=status,
        created_by="user-1",
        reviewed_by=None,
        review_notes=None,
        created_at=now,
        updated_at=now,
        reviewed_at=None,
        published_at=None,
    )


def make_service() -> tuple[ImpactService, Mock]:
    repository = Mock()
    repository.is_authorized_orphanage_staff.return_value = True
    repository.create_update.side_effect = lambda update: update
    repository.get_update.return_value = make_update()
    repository.review_update.side_effect = (
        lambda update_id, decision, reviewer_id, review_notes: make_update(
            ImpactUpdateStatus(decision)
        )
    )
    return ImpactService(repository), repository


def test_valid_jpeg_media_is_accepted() -> None:
    media_type, extension = validate_media_payload(
        "image/jpeg",
        b"\xff\xd8\xff" + b"jpeg-data",
    )
    assert media_type == ImpactMediaType.IMAGE
    assert extension == ".jpg"


@pytest.mark.parametrize(
    ("content_type", "data"),
    [
        ("image/gif", b"GIF89a"),
        ("image/png", b"not-a-png"),
        ("video/mp4", b"not-an-mp4"),
        (None, b"content"),
        ("image/jpeg", b""),
    ],
)
def test_invalid_media_is_rejected(
    content_type: str | None,
    data: bytes,
) -> None:
    with pytest.raises(ValueError):
        validate_media_payload(content_type, data)


def test_create_update_starts_in_pending_review() -> None:
    service, repository = make_service()
    request = ImpactUpdateCreateRequest(
        title="Community progress",
        content="An update about recent community work.",
    )

    result = service.create_update(make_user(), "org-1", request)

    assert result.status == ImpactUpdateStatus.PENDING_REVIEW
    repository.create_update.assert_called_once()


def test_staff_cannot_create_update_for_another_organization() -> None:
    service, repository = make_service()
    request = ImpactUpdateCreateRequest(
        title="Community progress",
        content="An update about recent community work.",
    )

    with pytest.raises(PermissionError):
        service.create_update(make_user(), "org-2", request)

    repository.create_update.assert_not_called()


def test_non_admin_cannot_list_pending_updates() -> None:
    service, repository = make_service()

    with pytest.raises(PermissionError):
        service.list_pending_updates(make_user())

    repository.list_pending_updates.assert_not_called()


def test_approval_requires_privacy_confirmation() -> None:
    service, repository = make_service()
    request = ImpactReviewRequest(
        decision=ImpactReviewDecision.APPROVE,
        privacy_confirmed=False,
    )

    with pytest.raises(ValueError, match="Privacy confirmation"):
        service.review_update(
            make_user(Role.CARELIFE_ADMIN, None),
            "update-1",
            request,
        )

    repository.review_update.assert_not_called()


def test_admin_can_approve_after_privacy_confirmation() -> None:
    service, repository = make_service()
    request = ImpactReviewRequest(
        decision=ImpactReviewDecision.APPROVE,
        privacy_confirmed=True,
    )

    result = service.review_update(
        make_user(Role.CARELIFE_ADMIN, None),
        "update-1",
        request,
    )

    assert result.status == ImpactUpdateStatus.APPROVED
    repository.review_update.assert_called_once_with(
        update_id="update-1",
        decision="approved",
        reviewer_id="user-1",
        review_notes=None,
    )


def test_rejection_requires_a_reason() -> None:
    service, repository = make_service()
    request = ImpactReviewRequest(
        decision=ImpactReviewDecision.REJECT,
        review_notes="   ",
    )

    with pytest.raises(ValueError, match="reason is required"):
        service.review_update(
            make_user(Role.CARELIFE_ADMIN, None),
            "update-1",
            request,
        )

    repository.review_update.assert_not_called()
