
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.domain.entities.caregiver import (
    CaregiverDocument,
    CaregiverProfile,
    CaregiverPublicProfile,
    CaregiverType,
    CaregiverVerificationStatus,
)


class CaregiverProfileCreateRequest(BaseModel):
    service_type: CaregiverType

    bio: str | None = Field(
        default=None,
        max_length=2000,
    )

    experience_years: int = Field(
        default=0,
        ge=0,
        le=60,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )


class CaregiverProfileUpdateRequest(BaseModel):
    service_type: CaregiverType | None = None

    bio: str | None = Field(
        default=None,
        max_length=2000,
    )

    experience_years: int | None = Field(
        default=None,
        ge=0,
        le=60,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )


class CaregiverDocumentSubmitRequest(BaseModel):
    document_type: Literal[
        "identity",
        "qualification",
    ]

    document_reference: str = Field(
        min_length=1,
        max_length=2000,
    )

    @field_validator("document_reference")
    @classmethod
    def validate_document_reference(
        cls,
        value: str,
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Document reference is required."
            )

        return value


class CaregiverVerificationDecisionRequest(BaseModel):
    status: Literal["approved", "rejected"]

    message: str | None = Field(
        default=None,
        max_length=2000,
    )


class CaregiverDocumentResponse(BaseModel):
    id: str
    document_type: str
    document_reference: str
    submitted_at: datetime

    @classmethod
    def from_entity(
        cls,
        document: CaregiverDocument,
    ) -> "CaregiverDocumentResponse":
        return cls(
            id=document.id,
            document_type=document.document_type.value,
            document_reference=document.document_reference,
            submitted_at=document.submitted_at,
        )


class CaregiverProfileResponse(BaseModel):
    user_id: str
    full_name: str | None = None
    phone: str | None = None

    service_type: CaregiverType
    bio: str | None = None
    experience_years: int
    location: str | None = None

    verification_status: CaregiverVerificationStatus
    review_message: str | None = None
    reviewed_at: datetime | None = None

    created_at: datetime
    updated_at: datetime

    documents: list[CaregiverDocumentResponse] = Field(
        default_factory=list
    )

    @classmethod
    def from_entity(
        cls,
        profile: CaregiverProfile,
    ) -> "CaregiverProfileResponse":
        return cls(
            user_id=profile.user_id,
            full_name=profile.full_name,
            phone=profile.phone,
            service_type=profile.service_type,
            bio=profile.bio,
            experience_years=profile.experience_years,
            location=profile.location,
            verification_status=profile.verification_status,
            review_message=profile.review_message,
            reviewed_at=profile.reviewed_at,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            documents=[
                CaregiverDocumentResponse.from_entity(document)
                for document in profile.documents
            ],
        )


class CaregiverPublicProfileResponse(BaseModel):
    caregiver_id: str
    full_name: str | None = None
    service_type: CaregiverType
    bio: str | None = None
    experience_years: int
    location: str | None = None

    @classmethod
    def from_entity(
        cls,
        profile: CaregiverPublicProfile,
    ) -> "CaregiverPublicProfileResponse":
        return cls(
            caregiver_id=profile.caregiver_id,
            full_name=profile.full_name,
            service_type=profile.service_type,
            bio=profile.bio,
            experience_years=profile.experience_years,
            location=profile.location,
        )