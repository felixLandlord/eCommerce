from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas import UserInDB

router = APIRouter(prefix="/user", tags=["users"])

@router.get("/me", response_model=UserInDB)
async def read_users_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    return current_user