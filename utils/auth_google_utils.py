from starlette.requests import Request
from fastapi import APIRouter
from authlib.integrations.starlette_client import OAuth
from utils.auth_utils import TokenPair, create_access_token, create_refresh_token
import os
from services.users_services import UserService, get_user_service
from fastapi import Depends, HTTPException
from authlib.integrations.starlette_client import OAuthError
from datetime import timedelta

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    },
)

async def oauth_google_authorize_redirect(request: Request, redirect_uri: str):
    return await oauth.google.authorize_redirect(request, redirect_uri)

async def oauth_google_authorize_access_token(request: Request):
    return await oauth.google.authorize_access_token(request)
