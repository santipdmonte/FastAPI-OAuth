from starlette.requests import Request
from fastapi import APIRouter
from authlib.integrations.starlette_client import OAuth
import os


auth_google_router = APIRouter(prefix="/google")
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
    redirect_uri = request.url_for('auth_via_google')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@auth_google_router.get("/auth")
async def auth_via_google(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token['userinfo']
    return dict(user)