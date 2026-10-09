from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ImpactUpdateStatus(str, Enum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class ImpactMediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"


class ImpactReviewDecision(str, Enum):
    APPROVE = "approved"
    REJECT = "rejected"


class ImpactUpdate(BaseModel):
    id: str
    organization_id: str
    organization_name: str
    title: str
    content: str
    status: ImpactUpdateStatus
    created_by: str
    reviewed_by: str | None
    review_notes: str | None
    created_at: datetime
    updated_at: datetime
    reviewed_at: datetime | None
    published_at: datetime | None


class ImpactMedia(BaseModel):
    id: str
    update_id: str
    storage_key: str
    content_type: str
    media_type: ImpactMediaType
    file_size: int
    created_at: datetime