from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Product, User
from app.schemas import ProductCreate, ProductUpdate, ProductInDB

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=ProductInDB)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    db_product = Product(**product.dict(), owner_id=current_user.id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/", response_model=List[ProductInDB])
async def read_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=ProductInDB)
async def read_product(
    product_id: int,
    db: Session = Depends(get_db)
) -> Any:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductInDB)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    if db_product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    for field, value in product.dict(exclude_unset=True).items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}