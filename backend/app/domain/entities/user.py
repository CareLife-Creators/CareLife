from pydantic import BaseModel, Field


class User(BaseModel):
    id: str
    email: str
    password_hash: str
    role_name: str
    organization_id: str | None = None
    organization_ids: list[str] = Field(default_factory=list)
    organization_roles: dict[str, str] = Field(default_factory=dict)
    full_name: str | None = None
    phone: str | None = None
    is_active: bool = True
