from datetime import datetime, timedelta, timezone
import jwt
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import uuid

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

def _with_standard_claims(data: dict, *, token_type: str, exp_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + exp_delta
    jti = uuid.uuid4().hex
    to_encode.update({"exp": expire, "type": token_type, "jti": jti})
    return to_encode


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