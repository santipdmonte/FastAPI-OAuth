from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    disabled: bool = False
    email_verified: bool = False
    picture: str | None = None

class UserInDB(User):
    hashed_password: str