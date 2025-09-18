from fastapi import Depends, APIRouter
from typing import Annotated
from utils.jwt_utils import get_current_active_user
from schemas.users_schemas import UserBase, UserUpdate
from services.users_services import UserService, get_user_service

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.get("/")
async def get_all_users(
    user_service: UserService = Depends(get_user_service)
):
    return user_service.get_all_users()


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