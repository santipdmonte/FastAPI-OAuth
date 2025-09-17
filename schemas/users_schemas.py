from pydantic import BaseModel

class User(BaseModel):
    username: str
    full_name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    disabled: bool = False
    email_verified: bool = False
    picture: str | None = None

class UserInDB(User):
    hashed_password: str | None = None

class UserCreate(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    full_name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    picture: str | None = None