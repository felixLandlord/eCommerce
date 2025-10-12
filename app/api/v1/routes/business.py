from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Business, User
from app.schemas import BusinessCreate, BusinessUpdate, BusinessInDB

router = APIRouter(prefix="/business", tags=["business"])

@router.post("/", response_model=BusinessInDB)
async def create_business(
    business: BusinessCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    db_business = Business(**business.dict(), owner_id=current_user.id)
    db.add(db_business)
    db.commit()
    db.refresh(db_business)
    return db_business

@router.get("/", response_model=List[BusinessInDB])
async def read_businesses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    businesses = db.query(Business).offset(skip).limit(limit).all()
    return businesses

@router.get("/{business_id}", response_model=BusinessInDB)
async def read_business(
    business_id: int,
    db: Session = Depends(get_db)
) -> Any:
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@router.put("/{business_id}", response_model=BusinessInDB)
async def update_business(
    business_id: int,
    business: BusinessUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    db_business = db.query(Business).filter(Business.id == business_id).first()
    if not db_business:
        raise HTTPException(status_code=404, detail="Business not found")
    if db_business.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    for field, value in business.dict(exclude_unset=True).items():
        setattr(db_business, field, value)
    
    db.commit()
    db.refresh(db_business)
    return db_business

@router.delete("/{business_id}")
async def delete_business(
    business_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if business.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(business)
    db.commit()
    return {"message": "Business deleted successfully"}