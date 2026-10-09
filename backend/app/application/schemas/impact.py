from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.entities.impact import (
    ImpactMediaType,
    ImpactReviewDecision,
    ImpactUpdateStatus,
)


class ImpactUpdateCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=10, max_length=5000)

    @field_validator("title", "content")
    @classmethod
    def clean_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field is required")
        return value


class ImpactReviewRequest(BaseModel):
    decision: ImpactReviewDecision
    privacy_confirmed: bool = False
    review_notes: str | None = Field(default=None, max_length=2000)

    @field_validator("review_notes")
    @classmethod
    def clean_review_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


class ImpactMediaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    update_id: str
    media_type: ImpactMediaType
    content_type: str
    file_size: int
    url: str
    created_at: datetime


class ImpactUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    organization_name: str
    title: str
    content: str
    status: ImpactUpdateStatus
    created_at: datetime
    published_at: datetime | None
    media: list[ImpactMediaResponse] = Field(default_factory=list)