
from pathlib import Path
import re
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse

from app.application.schemas.caregiver import (
    CaregiverDocumentSubmitRequest,
    CaregiverProfileCreateRequest,
    CaregiverProfileResponse,
    CaregiverProfileUpdateRequest,
    CaregiverPublicProfileResponse,
    CaregiverVerificationDecisionRequest,
)
from app.application.use_cases.caregivers import CaregiverService
from app.core.caregiver_documents import (
    CAREGIVER_DOCUMENT_DIRECTORY,
    build_upload_reference,
    caregiver_document_path,
    parse_upload_reference,
)
from app.domain.entities.caregiver import CaregiverType
from app.domain.entities.user_context import Role, UserContext
from app.presentation.api.dependencies.authorization import require_role
from app.presentation.api.dependencies.caregiver import (
    get_caregiver_service,
)


MAX_CAREGIVER_DOCUMENT_BYTES = 10 * 1024 * 1024
CAREGIVER_DOCUMENT_TYPES = {
    "application/pdf": (".pdf", b"%PDF-"),
    "image/jpeg": (".jpg", b"\xff\xd8\xff"),
    "image/png": (".png", b"\x89PNG\r\n\x1a\n"),
    "image/webp": (".webp", None),
}


def _document_file_response(document):
    upload = parse_upload_reference(document.document_reference)
    if upload is None:
        raise HTTPException(404, detail="No uploaded file is attached to this document.")
    storage_key, filename = upload
    path = caregiver_document_path(storage_key)
    if not path.is_file():
        raise HTTPException(404, detail="The uploaded document could not be found.")
    content_type = {
        ".pdf": "application/pdf",
        ".jpg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }[Path(storage_key).suffix.lower()]
    return FileResponse(path, media_type=content_type, filename=filename)


def _validate_caregiver_document(content_type, data):
    normalized_type = (content_type or "").split(";", 1)[0].strip().lower()
    supported = CAREGIVER_DOCUMENT_TYPES.get(normalized_type)
    if supported is None:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Upload a PDF, JPG, PNG or WebP document.",
        )
    extension, signature = supported
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="The selected file is empty.")
    if normalized_type == "image/webp":
        valid = len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    else:
        valid = data.startswith(signature)
    if not valid:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="The file content does not match its declared file type.",
        )
    return extension


def _safe_document_filename(filename, extension):
    candidate = Path((filename or "").replace("\\", "/")).name
    candidate = re.sub(r"[^A-Za-z0-9._ -]", "_", candidate).strip(" .")
    candidate = candidate[:180]
    return candidate or "caregiver-document" + extension

router = APIRouter(
    prefix="/caregivers",
    tags=["Caregiver Profiles and Verification"],
)


@router.post(
    "/me/profile",
    response_model=CaregiverProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_my_profile(
    request: CaregiverProfileCreateRequest,
    current_user: UserContext = Depends(
        require_role(Role.INDEPENDENT_CAREGIVER)
    ),
    service: CaregiverService = Depends(get_caregiver_service),
):
    try:
        profile = service.create_profile(current_user, request)
        return CaregiverProfileResponse.from_entity(profile)
    except PermissionError as exc:
        raise HTTPException(403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, detail=str(exc)) from exc


@router.get(
    "/me/profile",
    response_model=CaregiverProfileResponse,
)
def get_my_profile(
    current_user: UserContext = Depends(
        require_role(Role.INDEPENDENT_CAREGIVER)
    ),
    service: CaregiverService = Depends(get_caregiver_service),
):
    try:
        profile = service.get_my_profile(current_user)
        return CaregiverProfileResponse.from_entity(profile)
    except PermissionError as exc:
        raise HTTPException(403, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, detail=str(exc)) from exc


@router.patch(
    "/me/profile",
    response_model=CaregiverProfileResponse,
)
def update_my_profile(
    request: CaregiverProfileUpdateRequest,
    current_user: UserContext = Depends(
        require_role(Role.INDEPENDENT_CAREGIVER)
    ),
    service: CaregiverService = Depends(get_caregiver_service),
):
    try:
        profile = service.update_profile(current_user, request)
        return CaregiverProfileResponse.from_entity(profile)
    except PermissionError as exc:
        raise HTTPException(403, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, detail=str(exc)) from exc


@router.post(
    "/me/profile/documents",
    response_model=CaregiverProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_my_document(
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: UserContext = Depends(
        require_role(Role.INDEPENDENT_CAREGIVER)
    ),
    service: CaregiverService = Depends(get_caregiver_service),
):
    storage_path = None
    try:
        data = await file.read(MAX_CAREGIVER_DOCUMENT_BYTES + 1)
        if len(data) > MAX_CAREGIVER_DOCUMENT_BYTES:
            raise HTTPException(
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="The document must be 10 MB or smaller.",
            )
        extension = _validate_caregiver_document(file.content_type, data)
        filename = _safe_document_filename(file.filename, extension)
        storage_key = uuid4().hex + extension
        CAREGIVER_DOCUMENT_DIRECTORY.mkdir(parents=True, exist_ok=True)
        storage_path = caregiver_document_path(storage_key)
        storage_path.write_bytes(data)
        request = CaregiverDocumentSubmitRequest(
            document_type=document_type,
            document_reference=build_upload_reference(storage_key, filename),
        )
        profile = service.submit_document(current_user, request)
        return CaregiverProfileResponse.from_entity(profile)
    except HTTPException:
        if storage_path and storage_path.exists():
            storage_path.unlink()
        raise
    except PermissionError as exc:
        if storage_path and storage_path.exists():
            storage_path.unlink()
        raise HTTPException(403, detail=str(exc)) from exc
    except LookupError as exc:
        if storage_path and storage_path.exists():
            storage_path.unlink()
        raise HTTPException(404, detail=str(exc)) from exc
    except ValueError as exc:
        if storage_path and storage_path.exists():
            storage_path.unlink()
        raise HTTPException(422, detail=str(exc)) from exc
    except Exception:
        if storage_path and storage_path.exists():
            storage_path.unlink()
        raise
    finally:
        await file.close()


@router.get(
    "/me/profile/documents/{document_id}/file",
)
def download_my_document(
    document_id: str,
    current_user: UserContext = Depends(
        require_role(Role.INDEPENDENT_CAREGIVER)
    ),
    service: CaregiverService = Depends(get_caregiver_service),
):
    try:
        profile = service.get_my_profile(current_user)
        document = next((item for item in profile.documents if item.id == document_id), None)
        if document is None:
            raise HTTPException(404, detail="Document not found.")
        return _document_file_response(document)
    except PermissionError as exc:
        raise HTTPException(403, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, detail=str(exc)) from exc


@router.get(
    "/{caregiver_id}/documents/{document_id}/file",
)
def download_caregiver_document_for_admin(
    caregiver_id: str,
    document_id: str,
    current_user: UserContext = Depends(
        require_role(Role.CARELIFE_ADMIN)
    ),
    service: CaregiverService = Depends(get_caregiver_service),
):
    try:
        profile = service.get_profile_for_admin(current_user, caregiver_id)
        document = next((item for item in profile.documents if item.id == document_id), None)
        if document is None:
            raise HTTPException(404, detail="Document not found.")
        return _document_file_response(document)
    except PermissionError as exc:
        raise HTTPException(403, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, detail=str(exc)) from exc


@router.get(
    "/verification/pending",
    response_model=list[CaregiverProfileResponse],
)
def list_pending_caregivers(
    current_user: UserContext = Depends(
        require_role(Role.CARELIFE_ADMIN)
    ),
    service: CaregiverService = Depends(get_caregiver_service),
):
    profiles = service.list_pending_profiles(current_user)

    return [
        CaregiverProfileResponse.from_entity(profile)
        for profile in profiles
    ]


@router.post(
    "/{caregiver_id}/verification",
    response_model=CaregiverProfileResponse,
)
def review_caregiver(
    caregiver_id: str,
    request: CaregiverVerificationDecisionRequest,
    current_user: UserContext = Depends(
        require_role(Role.CARELIFE_ADMIN)
    ),
    service: CaregiverService = Depends(get_caregiver_service),
):
    try:
        profile = service.review_profile(
            current_user,
            caregiver_id,
            request,
        )
        return CaregiverProfileResponse.from_entity(profile)
    except PermissionError as exc:
        raise HTTPException(403, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, detail=str(exc)) from exc


@router.get(
    "",
    response_model=list[CaregiverPublicProfileResponse],
)
def list_public_caregivers(
    search: str | None = Query(default=None, max_length=100),
    location: str | None = Query(default=None, max_length=100),
    service_type: CaregiverType | None = Query(default=None),
    service: CaregiverService = Depends(get_caregiver_service),
):
    profiles = service.list_public_profiles(
        search=search,
        location=location,
        service_type=service_type,
    )

    return [
        CaregiverPublicProfileResponse.from_entity(profile)
        for profile in profiles
    ]


@router.get(
    "/{caregiver_id}",
    response_model=CaregiverPublicProfileResponse,
)
def get_public_caregiver(
    caregiver_id: str,
    service: CaregiverService = Depends(get_caregiver_service),
):
    try:
        profile = service.get_public_profile(caregiver_id)
        return CaregiverPublicProfileResponse.from_entity(profile)
    except LookupError as exc:
        raise HTTPException(404, detail=str(exc)) from exc