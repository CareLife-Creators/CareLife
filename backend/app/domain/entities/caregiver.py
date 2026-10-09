
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class CaregiverType(str, Enum):
    NANNY = "nanny"
    ELDER_CARE_GIVER = "elder_care_giver"


class CaregiverVerificationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CaregiverDocumentType(str, Enum):
    IDENTITY = "identity"
    QUALIFICATION = "qualification"


class CaregiverDocument(BaseModel):
    id: str
    document_type: CaregiverDocumentType
    document_reference: str
    submitted_at: datetime


class CaregiverProfile(BaseModel):
    user_id: str
    full_name: str | None = None
    phone: str | None = None

    service_type: CaregiverType
    bio: str | None = None
    experience_years: int = Field(ge=0)
    location: str | None = None

    verification_status: CaregiverVerificationStatus
    review_message: str | None = None
    reviewed_at: datetime | None = None

    created_at: datetime
    updated_at: datetime

    documents: list[CaregiverDocument] = Field(
        default_factory=list
    )


class CaregiverPublicProfile(BaseModel):
    caregiver_id: str
    full_name: str | None = None
    service_type: CaregiverType
    bio: str | None = None
    experience_years: int
    location: str | None = None