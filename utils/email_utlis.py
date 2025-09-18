from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import os
import certifi
from datetime import timedelta
from utils.auth_utils import create_email_verified_token
from schemas.users_schemas import User
from services.users_services import get_user_service, UserService
from fastapi import Depends


email_router = APIRouter(prefix="/email")

# Email settings (example with Gmail SMTP)
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_REPLY_TO = os.getenv("SMTP_REPLY_TO")
EMAIL_TOKEN_EXPIRE_MINUTES = os.getenv("EMAIL_TOKEN_EXPIRE_MINUTES")
URL = os.getenv("URL")

class EmailRequest(BaseModel):
    email: EmailStr

def send_verification_email(email: str, token: str):
    try:
        # Create the email content
        message = MIMEMultipart()
        message["From"] = SMTP_USER
        message["To"] = email
        message["Subject"] = f"Your Verification Link"
        message["Reply-To"] = SMTP_REPLY_TO

        body = f"{URL}/auth/email/verify-token/?token={token}"
        message.attach(MIMEText(body, "plain"))

        # Connect to SMTP server
        context = ssl.create_default_context(cafile=certifi.where())
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls(context=context)
        server.login(SMTP_USER, SMTP_PASSWORD)

        # Send email
        server.sendmail(SMTP_USER, email, message.as_string())
        server.quit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email failed: {str(e)}")


def generate_email_verified_token(user: User):
    access_token_expires = timedelta(minutes=int(EMAIL_TOKEN_EXPIRE_MINUTES))
    access_token = create_email_verified_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return access_token


@email_router.post("/send-code/")
async def send_code(request: EmailRequest, background_tasks: BackgroundTasks, user_service: UserService = Depends(get_user_service)):
    user = user_service.get_user(request.email)
    if not user:
        user =user_service.create_user_with_email(request.email)
    token = generate_email_verified_token(user)

    background_tasks.add_task(send_verification_email, request.email, token)

    return {"message": "Verification code sent", "email": request.email}