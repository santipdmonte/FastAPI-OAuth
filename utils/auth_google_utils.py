from starlette.requests import Request
from fastapi import APIRouter
from authlib.integrations.starlette_client import OAuth
from utils.auth_utils import Token, create_access_token
import os
from services.users_services import UserService, get_user_service
from fastapi import Depends, HTTPException
from authlib.integrations.starlette_client import OAuthError
from datetime import timedelta

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

auth_google_router = APIRouter(prefix="/auth/google", tags=["auth"])
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

@auth_google_router.get("/login")
async def login_via_google(request: Request):
    redirect_uri = request.url_for('callback_via_google')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@auth_google_router.get("/callback")
async def callback_via_google(request: Request, user_service: UserService = Depends(get_user_service)):
    """
    Callback function for Google OAuth
    :param request: Request object
    :param user_service: User service

    Validate the request, get the google acces token (only validate login, we are not storing the google access token)
    create a new app access token

    :return: Token
    """
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    if not token:
        raise HTTPException(status_code=400, detail="No token returned from Google")
    
    user_service.process_google_login(token['userinfo'])

    # Create new app access token
    user_info = token['userinfo']
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_info['email']}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
