from pydantic import BaseModel
from datetime import datetime
from models.users_models import AuthProviderType, UserRole

class UserBase(BaseModel):
    email: str
    full_name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    disabled: bool = False
    picture: str | None = None
    role: UserRole | None = None

class UserUpdate(BaseModel):
    full_name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    picture: str | None = None


class UserSocialAccountBase(BaseModel):
    user_id: str
    provider: AuthProviderType
    provider_id: str
    is_verified: bool | None = None
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    email: str | None = None
    picture: str | None = None
