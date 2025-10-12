from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password
from app.core.email import send_email
from app.models import User
from app.schemas import UserCreate, Token, UserVerify

router = APIRouter(tags=["authentication"])

@router.post("/register", response_model=UserCreate)
async def register(user: UserCreate, db: Session = Depends(get_db)) -> Any:
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        is_active=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Send verification email
    await send_email(user.email)
    return user

@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified"
        )
    
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer"
    }

@router.post("/verify-email")
async def verify_email(verification: UserVerify, db: Session = Depends(get_db)) -> Any:
    user = db.query(User).filter(User.email == verification.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    db.commit()
    return {"message": "Email verified successfully"}