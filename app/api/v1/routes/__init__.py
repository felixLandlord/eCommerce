from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import List

from .auth import router as auth_router
from .users import router as users_router  
from .products import router as products_router

# Export routers for use in main.py
router_prefix = "/api/v1"

__all__ = [
    "auth",
    "users",
    "products"
]