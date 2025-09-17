from fastapi import FastAPI, Request
from dotenv import load_dotenv
load_dotenv()
import os

from starlette.middleware.sessions import SessionMiddleware
from utils.auth_google import auth_google_router
from routes.users import users_router
from routes.auth import auth_router

app = FastAPI(prefix="/api")

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

app.include_router(auth_google_router)
app.include_router(auth_router)
app.include_router(users_router)


from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="static/")

@app.get("/")
async def login(request: Request):
    """
    :param request: An instance of the `Request` class, representing the incoming HTTP request.
    :return: A TemplateResponse object rendering the "login.html" template with the given request context.
    """
    return templates.TemplateResponse("pages/login.html", {"request": request})

@app.get("/welcome")
async def welcome(request: Request):
    """
    :param request: The incoming HTTP request containing session data.
    :return: A TemplateResponse object that renders the welcome page with the user's name or 'Guest' if not found.
    """
    name = request.session.get('user_name', 'Guest')
    context = {"request": request, "name": name}
    return templates.TemplateResponse("pages/welcome.html", context)