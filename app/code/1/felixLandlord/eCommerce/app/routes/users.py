from fastapi import APIRouter, Depends
from app.core.models import user_pydanticIn, Business
from app.core.dependencies import get_current_user

router = APIRouter()

@router.post("/me")
async def user_login(current_user: user_pydanticIn = Depends(get_current_user)):
    business = await Business.get(owner=current_user)
    logo = business.logo
    logo_path = "localhost:8000/static/images/"+logo
    
    return {
        "status": "success",
        "detail": "User logged in successfully",
        "data": {
            "username": current_user.username,
            "email": current_user.email,
            "verified": current_user.is_verified,
            "joined_date": current_user.join_date.strftime("%b %d %Y"),
            "logo_path": logo_path
        }
    }