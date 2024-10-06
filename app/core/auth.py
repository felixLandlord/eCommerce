from passlib.context import CryptContext
import jwt
from dotenv import dotenv_values
from app.core.models import User
from fastapi import status
from fastapi.exceptions import HTTPException

config_credentials = dotenv_values(".env")

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hashed_password(password):
    return pwd_context.hash(password)


async def verify_token(token: str):
    try:
        payload = jwt.decode(token, config_credentials["SECRET"], algorithms=["HS256"])
        user = await User.get(id=payload.get("id"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired", headers={"WWW-Authenticate": "Bearer"})