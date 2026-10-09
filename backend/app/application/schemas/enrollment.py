from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.entities.enrollment import (
    EnrollmentStatus,
)


class EnrollmentCreateRequest(BaseModel):
    child_id: str = Field(
        min_length=1,
        max_length=100,
    )

    daycare_organization_id: str = Field(
        min_length=1,
        max_length=100,
    )


class EnrollmentReviewRequest(BaseModel):
    status: EnrollmentStatus
    message: str | None = Field(
        default=None,
        max_length=500,
    )


class EnrollmentResponse(BaseModel):
    id: str
    child_id: str
    daycare_organization_id: str
    status: EnrollmentStatus
    requested_at: datetime
    reviewed_at: datetime | None
    reviewed_by: str | None
    cancelled_at: datetime | None
    decision_message: str | None

    @classmethod
    def from_entity(
        cls,
        enrollment,
    ) -> "EnrollmentResponse":
        return cls(
            id=enrollment.id,
            child_id=enrollment.child_id,
            daycare_organization_id=(
                enrollment.daycare_organization_id
            ),
            status=enrollment.status,
            requested_at=enrollment.requested_at,
            reviewed_at=enrollment.reviewed_at,
            reviewed_by=enrollment.reviewed_by,
            cancelled_at=enrollment.cancelled_at,
            decision_message=enrollment.decision_message,
        )