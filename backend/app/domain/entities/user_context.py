from enum import Enum

from pydantic import BaseModel, Field


class Role(str, Enum):
    PARENT_GUARDIAN = "parent_guardian"
    DAYCARE_STAFF = "daycare_staff"
    INDEPENDENT_CAREGIVER = "independent_caregiver"
    DONOR_SUPPORTER = "donor_supporter"
    ORPHANAGE_STAFF = "orphanage_staff"
    FAMILY_REPRESENTATIVE = "family_representative"
    CARE_HOME_STAFF = "care_home_staff"
    CARELIFE_ADMIN = "carelife_admin"


class UserContext(BaseModel):
    user_id: str
    role: Role
    organization_id: str | None = None
    organization_ids: list[str] = Field(default_factory=list)