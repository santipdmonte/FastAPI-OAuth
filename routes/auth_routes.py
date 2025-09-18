from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from utils.auth_utils import Token, create_access_token
from services.users_services import get_user_service, UserService
from datetime import timedelta
import os
from utils.jwt_utils import validate_email_verified_token
from utils.email_utlis import generate_email_verified_token, send_verification_email, EmailRequest
from models.users_models import User

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login")
async def send_token(request: EmailRequest, background_tasks: BackgroundTasks, user_service: UserService = Depends(get_user_service)):
    user = user_service.get_user(request.email)
    if not user:
        user = User(email=request.email)
        user = user_service.create_user(user)
    token = generate_email_verified_token(user)

    background_tasks.add_task(send_verification_email, request.email, token)

    return {"message": "Verification code sent", "email": request.email}


@auth_router.get("/email/verify-token/")
async def verify_email_token(token: str, user_service: UserService = Depends(get_user_service)):
    user = validate_email_verified_token(token, user_service)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
