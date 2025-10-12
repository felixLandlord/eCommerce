from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from tortoise.contrib.fastapi import register_tortoise
from app.api.v1.routes import auth, users, products, uploads, business

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# Register Tortoise ORM
register_tortoise(
    app,
    db_url='sqlite://app/db/db.sqlite3',
    modules={'models': ['app.core.models']},
    generate_schemas=True,
    add_exception_handlers=True,
)

# Include routers from modular route files
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(products.router, prefix="/api/v1", tags=["products"]) 
app.include_router(uploads.router, prefix="/api/v1", tags=["uploads"])
app.include_router(business.router, prefix="/api/v1", tags=["business"])

# Root endpoint redirects to docs
@app.get("/")
async def root():
    return {"message": "Welcome to the eCommerce API. Visit /docs for documentation."}