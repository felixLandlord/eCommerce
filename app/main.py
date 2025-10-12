from fastapi import FastAPI, Request, HTTPException, status, Depends, responses
from tortoise import models
from tortoise.contrib.fastapi import register_tortoise
from app.core.models import user_pydantic, user_pydanticIn, user_pydanticOut, business_pydantic, business_pydanticIn, product_pydantic, product_pydanticIn, User, Business, Product
from datetime import datetime, timezone

# authentication
from app.core.auth import get_hashed_password, verify_token, token_generator
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt

# signals
from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient
from pydantic import BaseModel
from app.core.email import send_email

# response classes
from fastapi.responses import HTMLResponse

# templates
from fastapi.templating import Jinja2Templates

# image upload
from fastapi import File, UploadFile
import secrets
from fastapi.staticfiles import StaticFiles
from PIL import Image

# Import route modules
from app.api.v1.routes import auth, users, products

from dotenv import dotenv_values
config_credentials = dotenv_values(".env")

templates = Jinja2Templates(directory="app/templates")

app = FastAPI()

oauth2 = OAuth2PasswordBearer(tokenUrl="token")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

register_tortoise(
    app,
    db_url='sqlite://app/db/db.sqlite3',
    modules={'models': ['app.core.models']},
    generate_schemas=True,
    add_exception_handlers=True,
)

# Include routers from modules
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")

@app.get("/")
async def index() -> responses.RedirectResponse:
    return responses.RedirectResponse("/docs")

@post_save(User)
async def create_business(
    sender: "Type[User]",
    instance: User,
    created: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fields: List[str]
) -> None:
    if created:
        business_obj = await Business.create(
            business_name=instance.username, owner=instance
        )
        await business_pydantic.from_tortoise_orm(business_obj)
        print(f"Business created for user {instance.username}")
        # send the email
        await send_email([instance.email], instance)

@app.put("/business/{id}")
async def update_business(id: int, update_business: business_pydanticIn, current_user: user_pydanticIn = Depends(get_current_user)):
    business = await Business.get(id=id)
    business_owner = await business.owner
    
    update_business = update_business.dict(exclude_unset=True)
    
    if current_user == business_owner:
        business = await business.update_from_dict(update_business)
        await business.save()
        response = await business_pydantic.from_tortoise_orm(business)
        return {"status": "success", "detail": "Business updated successfully", "data": response}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not allowed to perform this action",
            headers={"WWW-Authenticate": "Bearer"},
        )