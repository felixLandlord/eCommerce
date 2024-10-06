from fastapi import FastAPI, Request, HTTPException, status
from tortoise import models
from tortoise.contrib.fastapi import register_tortoise
from app.core.models import user_pydantic, user_pydanticIn, user_pydanticOut, business_pydantic, business_pydanticIn, product_pydantic, product_pydanticIn, User, Business, Product
from app.core.auth import get_hashed_password, verify_token

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

templates = Jinja2Templates(directory="app/templates")

app = FastAPI()

register_tortoise(
    app,
    db_url='sqlite://app/db/db.sqlite3',
    modules={'models': ['app.core.models']},
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.get("/")
async def index():
    return {"Message": "Hello world"}


@app.post("/register")
async def register(user: user_pydanticIn):
    user_info = user.dict(exclude_unset=True)
    user_info['password'] = get_hashed_password(user_info['password'])
    user_obj = await User.create(**user_info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)
    return {
        "message": "User created successfully",
        "user": f"Hello {new_user.username}, check your email inbox for a link to verify your account. Thank You"
    }


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


@app.get("/verify-email", response_class=HTMLResponse)
async def email_verification(request: Request, token: str):
    user = await verify_token(token)
    
    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        print("Email verified successfully. You can now login to your account")
        return templates.TemplateResponse("verified.html", {"request": request, "username": user.username})

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired", headers={"WWW-Authenticate": "Bearer"})