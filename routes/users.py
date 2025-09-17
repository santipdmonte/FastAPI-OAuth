from fastapi import Depends, APIRouter
from typing import Annotated
from utils.jwt_utils import get_current_active_user
from schemas.users_schemas import User
from services.users_services import UserService, get_user_service

users_router = APIRouter(prefix="/users")


@users_router.get("/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@users_router.get("/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@users_router.get("/")
async def get_all_users(
    user_service: UserService = Depends(get_user_service)
):
    return user_service.get_all_users()