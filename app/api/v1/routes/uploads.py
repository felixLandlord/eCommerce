from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Any
import shutil
import os

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User

router = APIRouter(prefix="/uploadfile", tags=["uploads"])

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
) -> Any:
    try:
        upload_dir = f"uploads/{current_user.id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_location = f"{upload_dir}/{file.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not upload file: {str(e)}"
        )
    
    return {"filename": file.filename, "location": file_location}