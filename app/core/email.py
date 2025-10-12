from fastapi import BackgroundTasks, UploadFile, File, Form, Depends, HTTPException, status
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi.templating import Jinja2Templates
from dotenv import dotenv_values
from pydantic import BaseModel, EmailStr
from typing import List
from app.core.models import User
import jwt
from datetime import datetime, timedelta, timezone
import os

# Constants
EMAIL_TEMPLATES_DIR = "app/templates/email"
templates = Jinja2Templates(directory=EMAIL_TEMPLATES_DIR)

config_credentials = dotenv_values(".env")

conf = ConnectionConfig(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USERNAME=config_credentials["EMAIL"],
    MAIL_PASSWORD=config_credentials["PASS"],
    MAIL_FROM=config_credentials["EMAIL"],
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

class EmailSchema(BaseModel):
    email: List[EmailStr]

async def send_email(email: List, instance: User):
    expiration = datetime.now(timezone.utc) + timedelta(minutes=3)
    token_data = {
        "id": instance.id,
        "username": instance.username,
        "exp": expiration
    }
    
    token = jwt.encode(token_data, config_credentials["SECRET"], algorithm="HS256")
    
    # Render email template using Jinja2
    template = templates.get_template("verified.html")
    html_content = template.render(
        token=token,
        username=instance.username,
        verification_url=f"http://localhost:8000/verify-email/?token={token}"
    )

    message = MessageSchema(
        subject="miniShop Account Verification Email",
        recipients=email,
        body=html_content,
        subtype="html",
    )
    
    fm = FastMail(conf)
    await fm.send_message(message=message)