import re
from pathlib import Path

from app.core.config import BACKEND_DIR


CAREGIVER_DOCUMENT_DIRECTORY = (
    BACKEND_DIR / "uploads" / "caregiver_documents"
)
_UPLOAD_REFERENCE = re.compile(
    r"^upload:([a-f0-9]{32}\.(?:pdf|jpg|png|webp))\|(.{1,200})$"
)


def build_upload_reference(storage_key: str, filename: str) -> str:
    return f"upload:{storage_key}|{filename}"


def parse_upload_reference(value: str) -> tuple[str, str] | None:
    match = _UPLOAD_REFERENCE.fullmatch(value)
    if not match:
        return None
    return match.group(1), match.group(2)


def caregiver_document_path(storage_key: str) -> Path:
    return CAREGIVER_DOCUMENT_DIRECTORY / storage_key