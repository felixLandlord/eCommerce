from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone
from app.core.models import (
    product_pydantic,
    product_pydanticIn,
    Product,
    user_pydanticIn
)
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("")
async def add_new_product(
    product: product_pydanticIn,
    current_user: user_pydanticIn = Depends(get_current_user)
):
    product = product.dict(exclude_unset=True)

    if product['original_price'] > 0:
        product["percentage_discount"] = (
            (product["original_price"] - product['new_price']) / 
            product['original_price']
        ) * 100

    product_obj = await Product.create(**product, business=current_user)
    product_obj = await product_pydantic.from_tortoise_orm(product_obj)
    return {
        "status": "success",
        "detail": "Product added successfully",
        "data": product_obj
    }

@router.get("")
async def get_products():
    response = await product_pydantic.from_queryset(Product.all())
    return {"status": "success", "data": response}

@router.get("/{id}")
async def get_specific_product(id: int):
    product = await Product.get(id=id)
    business = await product.business
    owner = await business.owner
    response = await product_pydantic.from_queryset_single(Product.get(id=id))
    
    return {
        "status": "success",
        "data": {
            "product_details": response,
            "business_details": {
                "name": business.business_name,
                "city": business.city,
                "region": business.region,
                "description": business.description,
                "logo": business.logo,
                "owner_id": owner.id,
                "email": owner.email,
                "join_date": owner.join_date.strftime("%b %d %Y")
            }
        }
    }

@router.delete("/{id}")
async def delete_product(
    id: int,
    current_user: user_pydanticIn = Depends(get_current_user)
):
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

@router.put("/{id}")
async def update_product(
    id: int,
    update_info: product_pydanticIn,
    current_user: user_pydanticIn = Depends(get_current_user)
):
    product = await Product.get(id=id)
    business = await product.business
    owner = await business.owner
    
    update_info = update_info.dict(exclude_unset=True)
    update_info["date_published"] = datetime.now(timezone.utc)
    
    if current_user == owner and update_info["original_price"] > 0:
        update_info["percentage_discount"] = (
            (update_info["original_price"] - update_info["new_price"]) / 
            update_info["original_price"]
        ) * 100
        
        product = await product.update_from_dict(update_info)
        await product.save()
        response = await product_pydantic.from_tortoise_orm(product)
        return {
            "status": "success",
            "detail": "Product updated successfully",
            "data": response
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not allowed to perform this action or invalid user input",
        headers={"WWW-Authenticate": "Bearer"},
    )