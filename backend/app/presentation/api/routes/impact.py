from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse

from app.application.schemas.impact import (
    ImpactMediaResponse,
    ImpactReviewRequest,
    ImpactUpdateCreateRequest,
    ImpactUpdateResponse,
)
from app.application.use_cases.impact import MAX_VIDEO_BYTES, ImpactService
from app.domain.entities.impact import (
    ImpactMedia,
    ImpactUpdate,
    ImpactUpdateStatus,
)
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import require_role
from app.presentation.api.dependencies.impact import get_impact_service


router = APIRouter(tags=["Orphanage Impact Updates"])


def _media_response(
    media: ImpactMedia,
    update_status: ImpactUpdateStatus,
) -> ImpactMediaResponse:
    if update_status == ImpactUpdateStatus.PENDING_REVIEW:
        url = f"/admin/impact-updates/media/{media.id}/file"
    else:
        url = f"/impact-updates/media/{media.id}/file"

    return ImpactMediaResponse(
        id=media.id,
        update_id=media.update_id,
        media_type=media.media_type,
        content_type=media.content_type,
        file_size=media.file_size,
        url=url,
        created_at=media.created_at,
    )


def _update_response(
    update: ImpactUpdate,
    service: ImpactService,
) -> ImpactUpdateResponse:
    media = service.list_media(update.id)
    return ImpactUpdateResponse(
        id=update.id,
        organization_id=update.organization_id,
        organization_name=update.organization_name,
        title=update.title,
        content=update.content,
        status=update.status,
        created_at=update.created_at,
        published_at=update.published_at,
        media=[
            _media_response(item, update.status)
            for item in media
        ],
    )


def _raise_http_error(exc: Exception) -> None:
    if isinstance(exc, PermissionError):
        code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, LookupError):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ValueError):
        code = status.HTTP_400_BAD_REQUEST
    else:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
    raise HTTPException(status_code=code, detail=str(exc)) from exc


@router.post(
    "/organizations/{organization_id}/impact-updates",
    response_model=ImpactUpdateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_impact_update(
    organization_id: str,
    request: ImpactUpdateCreateRequest,
    current_user: UserContext = Depends(require_role(Role.ORPHANAGE_STAFF)),
    service: ImpactService = Depends(get_impact_service),
):
    try:
        update = service.create_update(current_user, organization_id, request)
        return _update_response(update, service)
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.post(
    "/organizations/{organization_id}/impact-updates/{update_id}/media",
    response_model=ImpactMediaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_impact_media(
    organization_id: str,
    update_id: str,
    file: UploadFile = File(...),
    current_user: UserContext = Depends(require_role(Role.ORPHANAGE_STAFF)),
    service: ImpactService = Depends(get_impact_service),
):
    try:
        data = bytearray()
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            data.extend(chunk)
            if len(data) > MAX_VIDEO_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Media file must not exceed 30 MB",
                )

        media = service.add_media(
            current_user,
            organization_id,
            update_id,
            file.filename,
            file.content_type,
            bytes(data),
        )
        return _media_response(media, ImpactUpdateStatus.PENDING_REVIEW)
    except HTTPException:
        raise
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)
    finally:
        await file.close()


@router.get(
    "/admin/impact-updates",
    response_model=list[ImpactUpdateResponse],
)
def list_pending_impact_updates(
    current_user: UserContext = Depends(require_role(Role.CARELIFE_ADMIN)),
    service: ImpactService = Depends(get_impact_service),
):
    try:
        updates = service.list_pending_updates(current_user)
        return [_update_response(update, service) for update in updates]
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.post(
    "/admin/impact-updates/{update_id}/review",
    response_model=ImpactUpdateResponse,
)
def review_impact_update(
    update_id: str,
    request: ImpactReviewRequest,
    current_user: UserContext = Depends(require_role(Role.CARELIFE_ADMIN)),
    service: ImpactService = Depends(get_impact_service),
):
    try:
        update = service.review_update(current_user, update_id, request)
        return _update_response(update, service)
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.get(
    "/admin/impact-updates/media/{media_id}/file",
)
def get_pending_review_media(
    media_id: str,
    current_user: UserContext = Depends(require_role(Role.CARELIFE_ADMIN)),
    service: ImpactService = Depends(get_impact_service),
):
    try:
        path, media = service.get_review_media_path(current_user, media_id)
        return FileResponse(
            path=Path(path),
            media_type=media.content_type,
            filename=f"impact-media-{media.id}",
            content_disposition_type="inline",
            headers={"X-Content-Type-Options": "nosniff"},
        )
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)


@router.get(
    "/organizations/{organization_id}/impact-updates",
    response_model=list[ImpactUpdateResponse],
)
def list_organization_public_updates(
    organization_id: str,
    service: ImpactService = Depends(get_impact_service),
):
    updates = service.list_public_updates(organization_id)
    return [_update_response(update, service) for update in updates]


@router.get(
    "/impact-updates",
    response_model=list[ImpactUpdateResponse],
)
def list_public_impact_updates(
    organization_id: str | None = Query(default=None, min_length=1),
    service: ImpactService = Depends(get_impact_service),
):
    updates = service.list_public_updates(organization_id)
    return [_update_response(update, service) for update in updates]


@router.get("/impact-updates/media/{media_id}/file")
def get_published_impact_media(
    media_id: str,
    service: ImpactService = Depends(get_impact_service),
):
    try:
        path, media = service.get_public_media_path(media_id)
        return FileResponse(
            path=Path(path),
            media_type=media.content_type,
            filename=f"impact-media-{media.id}",
            content_disposition_type="inline",
            headers={"X-Content-Type-Options": "nosniff"},
        )
    except (PermissionError, LookupError, ValueError) as exc:
        _raise_http_error(exc)
