from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from app.core import security
from app.core.email import send_email
from app.core.security import get_password_hash
from app.core.config import settings
from app.core.deps import get_db
from app.models import User
from app.schemas import UserCreate, Token, VerifyEmail

router = APIRouter()

@router.post("/register", response_model=Any)
async def register(user: UserCreate, db: Session = Depends(get_db)) -> Any:
    """
    Register new user.
    """
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Create new user
    new_user = User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        is_active=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Send verification email
    await send_email(
        subject="Verify your email",
        recipient=new_user.email,
        template_name="verified.html",
        context={
            "token": security.create_email_token(new_user.email),
            "user": new_user
        }
    )
    
    return {"message": "User created. Please check your email to verify your account."}

@router.post("/verify-email")
async def verify_email(token_data: VerifyEmail, db: Session = Depends(get_db)) -> Any:
    """
    Verify user email with token.
    """
    email = security.verify_email_token(token_data.token)
    if not email:
        raise HTTPException(
            status_code=400,
            detail="Invalid token or token expired"
        )
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    if user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Email already verified"
        )
    
    user.is_active = True
    db.commit()
    
    return {"message": "Email verified successfully"}

@router.post("/token", response_model=Token)
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Email not verified"
        )
    
    return {
        "access_token": security.create_access_token(user.id),
        "token_type": "bearer",
    }