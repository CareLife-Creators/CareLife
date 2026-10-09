from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.application.interfaces.impact import ImpactRepository
from app.application.schemas.impact import (
ImpactReviewRequest,
ImpactUpdateCreateRequest,
)
from app.core.config import BACKEND_DIR
from app.domain.entities.impact import (
ImpactMedia,
ImpactMediaType,
ImpactReviewDecision,
ImpactUpdate,
ImpactUpdateStatus,
)
from app.domain.entities.user_context import Role, UserContext

MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_VIDEO_BYTES = 30 * 1024 * 1024

MEDIA_DIRECTORY = BACKEND_DIR / "uploads" / "impact_media"

SUPPORTED_MEDIA = {
"image/jpeg": (ImpactMediaType.IMAGE, ".jpg"),
"image/png": (ImpactMediaType.IMAGE, ".png"),
"image/webp": (ImpactMediaType.IMAGE, ".webp"),
"video/mp4": (ImpactMediaType.VIDEO, ".mp4"),
"video/quicktime": (ImpactMediaType.VIDEO, ".mov"),
"video/webm": (ImpactMediaType.VIDEO, ".webm"),
}

def validate_media_payload(
content_type: str | None,
data: bytes,
) -> tuple[ImpactMediaType, str]:
if not content_type:
raise ValueError("A supported media content type is required")

```
normalized_type = content_type.split(";", 1)[0].strip().lower()
supported = SUPPORTED_MEDIA.get(normalized_type)

if supported is None:
    raise ValueError(
        "Only JPEG, PNG, WebP, MP4, MOV and WebM are supported"
    )

media_type, extension = supported

if not data:
    raise ValueError("The uploaded media file is empty")

limit = (
    MAX_IMAGE_BYTES
    if media_type == ImpactMediaType.IMAGE
    else MAX_VIDEO_BYTES
)

if len(data) > limit:
    raise ValueError(
        f"This media type must not exceed {limit // (1024 * 1024)} MB"
    )

if normalized_type == "image/jpeg":
    valid_signature = data.startswith(b"\xff\xd8\xff")
elif normalized_type == "image/png":
    valid_signature = data.startswith(b"\x89PNG\r\n\x1a\n")
elif normalized_type == "image/webp":
    valid_signature = (
        len(data) >= 12
        and data[:4] == b"RIFF"
        and data[8:12] == b"WEBP"
    )
elif normalized_type in {"video/mp4", "video/quicktime"}:
    valid_signature = len(data) >= 12 and data[4:8] == b"ftyp"
else:
    valid_signature = data.startswith(b"\x1a\x45\xdf\xa3")

if not valid_signature:
    raise ValueError(
        "The file content does not match its declared media type"
    )

return media_type, extension
```

class ImpactService:
def **init**(self, repository: ImpactRepository):
self.repository = repository

```
@staticmethod
def _organization_access(
    user: UserContext,
    organization_id: str,
) -> bool:
    return (
        organization_id == user.organization_id
        or organization_id in user.organization_ids
    )

def _authorize_orphanage_staff(
    self,
    user: UserContext,
    organization_id: str,
) -> None:
    if user.role != Role.ORPHANAGE_STAFF:
        raise PermissionError("Orphanage staff access required")

    if not self._organization_access(user, organization_id):
        raise PermissionError(
            "You do not have access to this organization"
        )

    if not self.repository.is_authorized_orphanage_staff(
        organization_id,
        user.user_id,
    ):
        raise PermissionError(
            "Authorized orphanage staff membership is required"
        )

def create_update(
    self,
    user: UserContext,
    organization_id: str,
    request: ImpactUpdateCreateRequest,
) -> ImpactUpdate:
    self._authorize_orphanage_staff(user, organization_id)

    now = datetime.now(timezone.utc)

    update = ImpactUpdate(
        id=str(uuid4()),
        organization_id=organization_id,
        organization_name="",
        title=request.title,
        content=request.content,
        status=ImpactUpdateStatus.PENDING_REVIEW,
        created_by=user.user_id,
        reviewed_by=None,
        review_notes=None,
        created_at=now,
        updated_at=now,
        reviewed_at=None,
        published_at=None,
    )

    return self.repository.create_update(update)

def add_media(
    self,
    user: UserContext,
    organization_id: str,
    update_id: str,
    filename: str | None,
    content_type: str | None,
    data: bytes,
) -> ImpactMedia:
    # Never use the client-provided filename as a filesystem path.
    del filename

    self._authorize_orphanage_staff(user, organization_id)

    update = self.repository.get_update(update_id)

    if update is None:
        raise LookupError("Impact update not found")

    if update.organization_id != organization_id:
        raise PermissionError(
            "This update does not belong to the specified organization"
        )

    if update.status != ImpactUpdateStatus.PENDING_REVIEW:
        raise ValueError(
            "Media can only be added before moderation"
        )

    media_type, extension = validate_media_payload(
        content_type,
        data,
    )

    media_id = str(uuid4())
    storage_key = f"{uuid4().hex}{extension}"
    MEDIA_DIRECTORY.mkdir(parents=True, exist_ok=True)

    target = MEDIA_DIRECTORY / storage_key
    target.write_bytes(data)

    media = ImpactMedia(
        id=media_id,
        update_id=update_id,
        storage_key=storage_key,
        content_type=content_type.split(";", 1)[0].strip().lower(),
        media_type=media_type,
        file_size=len(data),
        created_at=datetime.now(timezone.utc),
    )

    try:
        # Pass the uploader's ID so the repository validates that user.
        return self.repository.add_media(
            organization_id,
            user.user_id,
            media,
        )
    except Exception:
        target.unlink(missing_ok=True)
        raise

def list_pending_updates(
    self,
    user: UserContext,
) -> list[ImpactUpdate]:
    if user.role != Role.CARELIFE_ADMIN:
        raise PermissionError(
            "CareLife administrator access required"
        )

    return self.repository.list_pending_updates()

def review_update(
    self,
    user: UserContext,
    update_id: str,
    request: ImpactReviewRequest,
) -> ImpactUpdate:
    if user.role != Role.CARELIFE_ADMIN:
        raise PermissionError(
            "CareLife administrator access required"
        )

    if request.decision == ImpactReviewDecision.APPROVE:
        if not request.privacy_confirmed:
            raise ValueError(
                "Privacy confirmation is required before publication"
            )
    elif not request.review_notes:
        raise ValueError(
            "A reason is required when rejecting an impact update"
        )

    updated = self.repository.review_update(
        update_id=update_id,
        decision=request.decision.value,
        reviewer_id=user.user_id,
        review_notes=request.review_notes,
    )

    if updated is None:
        raise LookupError("Impact update not found")

    return updated

def list_public_updates(
    self,
    organization_id: str | None = None,
) -> list[ImpactUpdate]:
    return self.repository.list_public_updates(organization_id)

def list_media(
    self,
    update_id: str,
) -> list[ImpactMedia]:
    return self.repository.list_media(update_id)

def get_public_media_path(
    self,
    media_id: str,
) -> tuple[Path, ImpactMedia]:
    media = self.repository.get_public_media(media_id)

    if media is None:
        raise LookupError("Published media not found")

    path = MEDIA_DIRECTORY / media.storage_key

    if path.resolve().parent != MEDIA_DIRECTORY.resolve():
        raise LookupError("Published media not found")

    if not path.is_file():
        raise LookupError("Published media file not found")

    return path, media
```
