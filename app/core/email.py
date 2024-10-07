from fastapi import BackgroundTasks, UploadFile, File, Form, Depends, HTTPException, status
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import dotenv_values
from pydantic import BaseModel, EmailStr
from typing import List
from app.core.models import User
import jwt
from datetime import datetime, timedelta, timezone


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
    
    template = f"""
        <!DOCTYPE html>
        <html>
            <head>
            </head>
            <body>
                <div style = "display: flex; align-items: center; justify-content: center; flex-direction: column">
                <h3>Account Verification</h3>
                <br>
                <p>Thanks for choosing miniShop. Please click on the link below to verify your account</p>
                <br>
                <a style = "margin-top: 1rem; padding: 1rem; border-readius: 0.5rem; font-size: 1rem; text-decoration: none; background: #0275d8; color: white;" href="http://localhost:8000/verify-email/?token={token}">
                Verify Email
                </a>
                <p>Please kindly ignore this email if you did not register for miniShop</p> 
                </div>
            </body>
        </html>
    """
    message = MessageSchema(
        subject="miniShop Account Verification Email",
        recipients=email,
        body=template,
        subtype="html",
    )
    
    fm = FastMail(conf)
    await fm.send_message(message=message)