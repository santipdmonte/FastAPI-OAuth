from fastapi import Depends, HTTPException
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from services.users_services import UserService, get_user_service
from schemas.users_schemas import User
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import status
import os
from pydantic import BaseModel

class TokenData(BaseModel):
    username: str | None = None

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def validate_email_verified_token(
    token: Annotated[str, Depends(oauth2_scheme)], 
    user_service: UserService = Depends(get_user_service)
):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("type") != "email_verified":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    username = payload.get("sub")
    user = user_service.get_user(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    user_service: UserService = Depends(get_user_service)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # TODO: Descomentar y Testear
        # if payload.get("type") != "access":
        #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    
    user = user_service.get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user