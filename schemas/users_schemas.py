from pydantic import BaseModel

class User(BaseModel):
    email: str
    full_name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    disabled: bool = False
    picture: str | None = None

class UserUpdate(BaseModel):
    full_name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    picture: str | None = None