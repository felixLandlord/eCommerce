from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import Any, List

from app.core.deps import get_current_user, get_db
from app.core.storage import save_upload_file
from app.models import User, Product
from app.schemas import ProductCreate, Product as ProductSchema

router = APIRouter()

@router.get("/products", response_model=List[ProductSchema])
def list_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve products.
    """
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@router.post("/products", response_model=ProductSchema)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create new product.
    """
    db_product = Product(**product.dict(), owner_id=current_user.id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/products/{id}", response_model=ProductSchema)
def read_product(
    id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get product by ID.
    """
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    return product

@router.put("/products/{id}", response_model=ProductSchema)
def update_product(
    id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update product.
    """
    db_product = db.query(Product).filter(Product.id == id).first()
    if not db_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    if db_product.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/products/{id}")
def delete_product(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Delete product.
    """
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    if product.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}

@router.post("/uploadfile/product/{id}")
async def upload_product_image(
    id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Upload product image.
    """
    product = db.query(Product).filter(Product.id == id).first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    if product.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    filename = await save_upload_file(
        upload_file=file,
        destination="products",
        filename=f"product_{id}"
    )
    
    product.image = filename
    db.commit()
    
    return {"filename": filename}