from hashlib import sha256
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.application.schemas.user_profile import (
    UserProfileResponse,
    UserProfileUpdateRequest,
)
from app.application.use_cases.user_profile import UserProfileService
from app.core.config import BACKEND_DIR
from app.domain.entities.user import User
from app.domain.entities.user_context import UserContext
from app.presentation.api.dependencies.authorization import (
    get_current_user,
)
from app.presentation.api.dependencies.user_profile import (
    get_user_profile_service,
)


router = APIRouter(
    prefix="/users/me/profile",
    tags=["User Profile"],
)

PROFILE_PHOTO_DIRECTORY = BACKEND_DIR / "uploads" / "profile_photos"
MAX_PROFILE_PHOTO_BYTES = 5 * 1024 * 1024
PROFILE_PHOTO_TYPES = {
    "image/jpeg": (".jpg", b"\xff\xd8\xff"),
    "image/png": (".png", b"\x89PNG\r\n\x1a\n"),
    "image/webp": (".webp", None),
}


def _photo_path(user_id: str) -> Path | None:
    user_key = sha256(user_id.encode("utf-8")).hexdigest()
    return next(PROFILE_PHOTO_DIRECTORY.glob(user_key + ".*"), None) if PROFILE_PHOTO_DIRECTORY.exists() else None


def to_profile_response(user: User) -> UserProfileResponse:
    return UserProfileResponse(
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role_name,
        profile_photo_url="/users/me/profile/photo",
    )


@router.get(
    "",
    response_model=UserProfileResponse,
)
def get_my_profile(
    current_user: UserContext = Depends(get_current_user),
    service: UserProfileService = Depends(
        get_user_profile_service
    ),
) -> UserProfileResponse:
    try:
        user = service.get_profile(current_user.user_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        ) from exc

    return to_profile_response(user)


@router.patch(
    "",
    response_model=UserProfileResponse,
)
def update_my_profile(
    request: UserProfileUpdateRequest,
    current_user: UserContext = Depends(get_current_user),
    service: UserProfileService = Depends(
        get_user_profile_service
    ),
) -> UserProfileResponse:
    try:
        user = service.update_profile(
            current_user.user_id,
            request.model_dump(exclude_unset=True),
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return to_profile_response(user)


@router.get("/photo")
def get_my_profile_photo(
    current_user: UserContext = Depends(get_current_user),
):
    path = _photo_path(current_user.user_id)
    if path is None or not path.is_file():
        raise HTTPException(status_code=404, detail="No profile photo has been uploaded.")
    media_type = {".jpg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}.get(path.suffix)
    if not media_type:
        raise HTTPException(status_code=404, detail="Profile photo not found.")
    return FileResponse(path, media_type=media_type, headers={"Cache-Control": "private, no-store"})


@router.put("/photo", status_code=status.HTTP_204_NO_CONTENT)
async def upload_my_profile_photo(
    file: UploadFile = File(...),
    current_user: UserContext = Depends(get_current_user),
):
    try:
        content_type = (file.content_type or "").split(";", 1)[0].lower()
        photo_type = PROFILE_PHOTO_TYPES.get(content_type)
        if photo_type is None:
            raise HTTPException(status_code=415, detail="Choose a JPG, PNG or WebP photo.")
        data = await file.read(MAX_PROFILE_PHOTO_BYTES + 1)
        if not data or len(data) > MAX_PROFILE_PHOTO_BYTES:
            raise HTTPException(status_code=413 if data else 400, detail="Choose a photo under 5 MB.")
        extension, signature = photo_type
        valid = (len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP") if content_type == "image/webp" else data.startswith(signature)
        if not valid:
            raise HTTPException(status_code=415, detail="The file contents do not match an image file.")
        PROFILE_PHOTO_DIRECTORY.mkdir(parents=True, exist_ok=True)
        user_key = sha256(current_user.user_id.encode("utf-8")).hexdigest()
        for old_photo in PROFILE_PHOTO_DIRECTORY.glob(user_key + ".*"):
            old_photo.unlink()
        (PROFILE_PHOTO_DIRECTORY / (user_key + extension)).write_bytes(data)
    finally:
        await file.close()


@router.delete("/photo", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_profile_photo(
    current_user: UserContext = Depends(get_current_user),
):
    path = _photo_path(current_user.user_id)
    if path is not None and path.is_file():
        path.unlink()
