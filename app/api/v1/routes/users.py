from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Any

from app.core.deps import get_current_user, get_db
from app.core.storage import save_upload_file
from app.models import User
from app.schemas import User as UserSchema

router = APIRouter()

@router.get("/user/me", response_model=UserSchema)
def read_user_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.post("/uploadfile/profile")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Upload user profile picture.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    filename = await save_upload_file(
        upload_file=file,
        destination="profiles",
        filename=f"user_{current_user.id}"
    )
    
    current_user.profile_picture = filename
    db.commit()
    
    return {"filename": filename}