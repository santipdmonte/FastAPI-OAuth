from fastapi import Depends, APIRouter, HTTPException, status
from typing import Annotated
from dependencies import get_current_active_user, get_current_active_admin_user
from schemas.users_schemas import UserUpdate, UserResponse, UserSocialAccountBase
from services.users_services import UserService, get_user_service
from uuid import UUID
from models.users_models import User

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.get("/")
async def get_all_users(
    # current_admin_user: Annotated[UserBase, Depends(get_current_active_admin_user)],
    user_service: UserService = Depends(get_user_service)
):
    return user_service.get_all_users()

@users_router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(
    email: str,
    user_service: UserService = Depends(get_user_service),
):
    return user_service.get_user_by_email(email)

@users_router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    user = user_service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@users_router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    user = user_service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_service.delete_user(user)

@users_router.patch("/{user_id}/admin")
async def make_user_admin(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    user = user_service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_service.make_user_admin(user)

@users_router.get("/me/", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

@users_router.patch("/me/", response_model=UserResponse)
async def update_user(
    user: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: UserService = Depends(get_user_service),
):
    return user_service.update_user(current_user, user)

@users_router.get("/me/social-accounts/", response_model=list[UserSocialAccountBase])
async def get_user_social_accounts(
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: UserService = Depends(get_user_service),
):
    return user_service.get_user_social_accounts(current_user)