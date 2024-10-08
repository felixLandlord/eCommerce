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


@app.get("/")
async def index() -> responses.RedirectResponse:
    return responses.RedirectResponse("/docs")


@app.post("/register")
async def register(user: user_pydanticIn):
    user_info = user.dict(exclude_unset=True)
    user_info['password'] = get_hashed_password(user_info['password'])
    user_obj = await User.create(**user_info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)
    return {
        "status": "success",
        "detail": "User created successfully",
        "message": f"Hello {new_user.username}, check your email inbox for a link to verify your account. Thank You"
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
    print("token decoded successfully")
    
    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        print("Email verified successfully. You can now login to your account")
        return templates.TemplateResponse("verified.html", {"request": request, "username": user.username})

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired", headers={"WWW-Authenticate": "Bearer"})


async def get_current_user(token: str = Depends(oauth2)):
    try:
        payload = jwt.decode(token, config_credentials["SECRET"], algorithms=["HS256"])
        user = await User.get(id=payload.get("id"))
    
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await user


@app.post("/token")
async def generate_token(request_form: OAuth2PasswordRequestForm = Depends()):
    token = await token_generator(request_form.username, request_form.password)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/user/me")
async def user_login(current_user: user_pydanticIn = Depends(get_current_user)):
    business = await Business.get(owner=current_user)
    logo = business.logo
    logo_path = "localhost:8000/static/images/"+logo
    return {
        "status": "success",
        "detail": "User logged In successfully",
        "data": {
            "username": current_user.username,
            "email": current_user.email,
            "verified": current_user.is_verified,
            "joined_date": current_user.join_date.strftime("%b %d %Y"),
            "logo_path": logo_path
            # "business_name": business.business_name,
            # "products": [product.name for product in business.products]   
        }
    }


@app.post("/uploadfile/profile")
async def upload_profile(file: UploadFile = File(...), current_user: user_pydanticIn = Depends(get_current_user)):
    FILEPATH = "app/static/images/"
    filename = file.filename
    extension = filename.split(".")[1]
    
    if extension not in ["png", "jpg", "jpeg"]:
        return {"status": "error", "detail": "File extension not allowed"}
    
    token_name = secrets.token_hex(5)+"."+extension
    generated_name = FILEPATH + token_name
    file_content = await file.read()
    
    with open(generated_name, "wb") as file:
        file.write(file_content)
    
    # pillow
    img = Image.open(generated_name)
    img = img.resize((200, 200))
    img.save(generated_name)
    
    file.close()
    
    business = await Business.get(owner=current_user)
    owner = await business.owner
    
    if owner == current_user:
        business.logo = token_name
        await business.save()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not allowed to perform this action", headers={"WWW-Authenticate": "Bearer"})
        
    # current_user.profile_picture = token_name
    # await current_user.save()
    file_url = "localhost:8000" + generated_name[1:]
    return {"status": "success", "detail": "File uploaded successfully", "filename": file_url}


@app.post("/uploadfile/product/{id}")
async def upload_product(id: int, file: UploadFile = File(...), current_user: user_pydanticIn = Depends(get_current_user)):
    FILEPATH = "app/static/images/"
    filename = file.filename
    extension = filename.split(".")[1]
    
    if extension not in ["png", "jpg", "jpeg"]:
        return {"status": "error", "detail": "File extension not allowed"}
    
    token_name = secrets.token_hex(5)+"."+extension
    generated_name = FILEPATH + token_name
    file_content = await file.read()
    
    with open(generated_name, "wb") as file:
        file.write(file_content)
    
    # pillow
    img = Image.open(generated_name)
    img = img.resize((200, 200))
    img.save(generated_name)
    
    file.close()
    
    product = await Product.get(id=id)
    business = await product.business
    owner = await business.owner
    
    if owner == current_user:
        product.product_image = token_name
        await product.save()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not allowed to perform this action", headers={"WWW-Authenticate": "Bearer"})
        
    file_url = "localhost:8000" + generated_name[1:]
    return {"status": "success", "detail": "File uploaded successfully", "filename": file_url}


@app.post("/products")
async def add_new_product(product: product_pydanticIn, current_user: user_pydanticIn = Depends(get_current_user)):
    product = product.dict(exclude_unset=True)

    if product['original_price'] > 0:
        product["percentage_discount"] = ((product["original_price"] - product['new_price']) / product['original_price']) * 100

    product_obj = await Product.create(**product, business=current_user)
    product_obj = await product_pydantic.from_tortoise_orm(product_obj)
    return {"status": "success", "detail": "Product added successfully", "data": product_obj}


@app.get("/products")
async def get_products():
    response = await product_pydantic.from_queryset(Product.all())
    return {"status": "success", "data": response}


@app.get("/products/{id}")
async def get_specific_product(id: int):
    product = await Product.get(id=id)
    business = await product.business
    owner = await business.owner
    response = await product_pydantic.from_queryset_single(Product.get(id=id))
    print(type(response))
    return {"status": "success",
            "data":
                {
                    "product_details": response,
                    "business_details": {
                        "name": business.business_name,
                        "city": business.city,
                        "region": business.region,
                        "description": business.description,
                        "logo": business.logo,
                        "owner_id": owner.id,
                        "email": owner.email,
                        "join_date":  owner.join_date.strftime("%b %d %Y")
                    }
                }
            }


@app.delete("/products/{id}")
async def delete_product(id: int, current_user: user_pydanticIn = Depends(get_current_user)):
    product = await Product.get(id=id)
    business = await product.business
    owner = await business.owner
    if current_user == owner:
        product.delete()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not allowed to perform this action",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"status": "success"}


@app.put("/product/{id}")
async def update_product(id: int, update_info: product_pydanticIn, current_user: user_pydanticIn = Depends(get_current_user)):
    product = await Product.get(id=id)
    business = await product.business
    owner = await business.owner
    
    update_info = update_info.dict(exclude_unset=True)
    update_info["date_published"] = datetime.now(timezone.utc)
    if current_user == owner and update_info["original_price"] > 0:
        update_info["percentage_discount"] = ((update_info["original_price"] - update_info["new_price"]) / update_info["original_price"]) * 100
        product = await product.update_from_dict(update_info)
        await product.save()
        response = await product_pydantic.from_tortoise_orm(product)
        return {"status": "success", "detail": "Product updated successfully", "data": response}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not allowed to perform this action or invalid user input",
            headers={"WWW-Authenticate": "Bearer"},
        )


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