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
    organization_roles: dict[str, Role] = Field(default_factory=dict)

    def has_role(self, role: Role) -> bool:
        return self.role == role or role in self.organization_roles.values()

    def has_organization_role(self, role: Role, organization_id: str) -> bool:
        return (
            (self.role == role and organization_id in self.organization_ids)
            or self.organization_roles.get(organization_id) == role
        )

    def organization_role_for(self, organization_id: str) -> Role | None:
        role = self.organization_roles.get(organization_id)
        if role is not None:
            return role
        if self.role in {
            Role.DAYCARE_STAFF,
            Role.ORPHANAGE_STAFF,
            Role.CARE_HOME_STAFF,
        } and organization_id in self.organization_ids:
            return self.role
        return None
