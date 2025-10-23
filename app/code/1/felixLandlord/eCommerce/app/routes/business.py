from fastapi import APIRouter, HTTPException, status, Depends
from app.core.models import business_pydanticIn, business_pydantic, Business
from app.core.dependencies import get_current_user
from app.core.models import user_pydanticIn

router = APIRouter()

@router.put("/{id}")
async def update_business(
    id: int,
    update_business: business_pydanticIn,
    current_user: user_pydanticIn = Depends(get_current_user)
):
    business = await Business.get(id=id)
    business_owner = await business.owner
    
    update_business = update_business.dict(exclude_unset=True)
    
    if current_user == business_owner:
        business = await business.update_from_dict(update_business)
        await business.save()
        response = await business_pydantic.from_tortoise_orm(business)
        return {
            "status": "success",
            "detail": "Business updated successfully",
            "data": response
        }
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not allowed to perform this action",
        headers={"WWW-Authenticate": "Bearer"},
    )