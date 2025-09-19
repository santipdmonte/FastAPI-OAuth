from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta, timezone
from services.tokens_service import TokenService, get_token_service
from pydantic import BaseModel
from jwt.exceptions import InvalidTokenError
import jwt
import uuid
import os
from dotenv import load_dotenv

load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
EMAIL_TOKEN_EXPIRE_MINUTES=int(os.getenv("EMAIL_TOKEN_EXPIRE_MINUTES", "5"))
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

bearer_scheme = HTTPBearer( 
    scheme_name="Bearer Token",
    description="Enter your access token here"
)

# ========== HELPER FUNCTIONS ==================

def _with_standard_claims(data: dict, *, token_type: str, exp_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + exp_delta
    jti = uuid.uuid4().hex
    to_encode.update({"exp": expire, "type": token_type, "jti": jti})
    return to_encode

# ========== TOKEN CREATION FUNCTIONS ==================

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = _with_standard_claims(data, token_type="access", exp_delta=expires_delta)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_email_verified_token(data: dict, expires_delta: timedelta | None = None):
    if expires_delta is None:
        expires_delta = timedelta(minutes=EMAIL_TOKEN_EXPIRE_MINUTES)
    to_encode = _with_standard_claims(data, token_type="email_verified", exp_delta=expires_delta)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    if expires_delta is None:
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = _with_standard_claims(data, token_type="refresh", exp_delta=expires_delta)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ========== VALIDATION FUNCTIONS ==================

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