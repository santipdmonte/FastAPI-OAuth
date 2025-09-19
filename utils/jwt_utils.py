from jwt.exceptions import InvalidTokenError
import jwt
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.users_services import UserService, get_user_service
from services.tokens_service import TokenService, get_token_service


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

bearer_scheme = HTTPBearer( 
    scheme_name="Bearer Token",
    description="Enter your access token here"
)

def validate_access_token(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token type: {payload.get('token_type')}")
        return payload
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def validate_email_verified_token(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "email_verified":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token type: {payload.get('token_type')}")
        return payload
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def validate_refresh_token(
    refresh_token: str,
    token_service: TokenService = Depends(get_token_service),
):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token type: {payload.get('token_type')}")
        jti = payload.get("jti")
        if jti and token_service.is_blacklisted(jti):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")
        return payload
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

