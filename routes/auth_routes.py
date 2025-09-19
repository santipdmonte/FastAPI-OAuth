from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from datetime import datetime, timedelta
import os

from utils.jwt_utils import bearer_scheme, validate_refresh_token, validate_access_token, validate_email_verified_token
from utils.email_utlis import generate_email_verified_token, send_verification_email, EmailRequest
from utils.auth_utils import TokenPair, create_access_token, create_refresh_token

from services.tokens_service import get_token_service, TokenService
from services.users_services import get_user_service, UserService
from fastapi.security import HTTPAuthorizationCredentials
from models.token_models import TokenType
from models.users_models import User

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/login")
async def send_token(request: EmailRequest, background_tasks: BackgroundTasks, user_service: UserService = Depends(get_user_service)):
    user = user_service.get_user_by_email(request.email)
    if not user:
        user = User(email=request.email)
        user = user_service.create_user(user)
    token = generate_email_verified_token(user)

    background_tasks.add_task(send_verification_email, request.email, token)

    return {"message": "Verification code sent", "email": request.email}


@auth_router.get("/verify-token/")
async def verify_email_token(token: str, user_service: UserService = Depends(get_user_service)):
    payload = validate_email_verified_token(token, user_service)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"sub": payload.email}
    access_token = create_access_token(
        data=data, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data=data)
    return TokenPair(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@auth_router.post("/refresh")
async def refresh_tokens(
    refresh_token: str,
    user_service: UserService = Depends(get_user_service),
    token_service: TokenService = Depends(get_token_service),
):

    payload = validate_refresh_token(refresh_token, token_service)
    email = payload["email"]
    old_jti = payload["jti"]
    user = user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    # Rotate refresh token: blacklist the old refresh jti
    token_service.blacklist_token(
        jti=old_jti,
        token_type=TokenType.REFRESH,
        user_id=user.id,
        expires_at=datetime.fromtimestamp(payload["exp"]),
        reason="rotated",
    )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(data={"sub": user.email})

    return TokenPair(access_token=access_token, refresh_token=new_refresh_token, token_type="bearer")


@auth_router.post("/logout")
async def logout(
    refresh_token: str | None = None,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    token_service: TokenService = Depends(get_token_service),
    user_service: UserService = Depends(get_user_service),
):
    access_token = credentials.credentials
    try:
        token_data = validate_access_token(access_token)
        email = token_data.get("sub")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    user = user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    if refresh_token:
        payload_r = validate_refresh_token(refresh_token, token_service)
        r_jti = payload_r.get("jti")
        r_exp = payload_r.get("exp")
        if r_jti:
            token_service.blacklist_token(
                jti=r_jti,
                token_type=TokenType.REFRESH,
                user_id=user.id,
                expires_at=datetime.fromtimestamp(r_exp),
                reason="logout",
            )

    return {"message": "Logged out"}
