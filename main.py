from fastapi import FastAPI
import os

from starlette.middleware.sessions import SessionMiddleware
from utils.auth_google_utils import auth_google_router
from routes.users_routes import users_router
from routes.auth_routes import auth_router
from utils.email_utlis import email_router
from database import create_db_and_tables

create_db_and_tables()

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

app.include_router(auth_google_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(email_router)