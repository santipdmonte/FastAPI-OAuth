from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from utils.auth_utils import validate_access_token, bearer_scheme
from services.users_services import UserService, get_user_service
from models.users_models import User, UserRole
from typing import Annotated
from fastapi import status


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_service: UserService = Depends(get_user_service)
):
    token = credentials.credentials
    token_data = validate_access_token(token)
    email = token_data.get("sub")
    
    user = user_service.get_user_by_email(email=email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin user required")
    return current_user