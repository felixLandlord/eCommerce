from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
from app.core.models import user_pydanticIn, Business, Product
from app.core.dependencies import get_current_user
import secrets
from PIL import Image

router = APIRouter()

@router.post("/profile")
async def upload_profile(
    file: UploadFile = File(...),
    current_user: user_pydanticIn = Depends(get_current_user)
):
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
    
    # Resize image
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not allowed to perform this action",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    file_url = "localhost:8000" + generated_name[1:]
    return {
        "status": "success",
        "detail": "File uploaded successfully",
        "filename": file_url
    }

@router.post("/product/{id}")
async def upload_product(
    id: int,
    file: UploadFile = File(...),
    current_user: user_pydanticIn = Depends(get_current_user)
):
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
    
    # Resize image
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not allowed to perform this action",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    file_url = "localhost:8000" + generated_name[1:]
    return {
        "status": "success",
        "detail": "File uploaded successfully",
        "filename": file_url
    }