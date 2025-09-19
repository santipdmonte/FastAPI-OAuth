from fastapi import Depends, APIRouter, HTTPException, status
from typing import Annotated
from utils.jwt_utils import get_current_active_user, get_current_active_admin_user
from schemas.users_schemas import UserBase, UserUpdate
from services.users_services import UserService, get_user_service

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.get("/")
async def get_all_users(
    # current_admin_user: Annotated[UserBase, Depends(get_current_active_admin_user)],
    user_service: UserService = Depends(get_user_service)
):
    return user_service.get_all_users()

@users_router.patch("/admin/{user_id}")
async def make_user_admin(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
):
    user = user_service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_service.make_user_admin(user)


@users_router.get("/me/", response_model=UserBase)
async def read_users_me(
    current_user: Annotated[UserBase, Depends(get_current_active_user)],
):
    return current_user

@users_router.patch("/me/")
async def update_user(
    user: UserUpdate,
    current_user: Annotated[UserBase, Depends(get_current_active_user)],
    user_service: UserService = Depends(get_user_service),
):
    return user_service.update_user(current_user, user)

@users_router.get("/me/social-accounts/")
async def get_user_social_accounts(
    current_user: Annotated[UserBase, Depends(get_current_active_user)],
    user_service: UserService = Depends(get_user_service),
):
    return user_service.get_user_social_accounts(current_user.id)