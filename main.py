import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError

from app.config import settings
from app.database import SessionLocal, engine
from app.models import Base
from app.routers import auth, permissions, roles, users
from app.routers import lookup
from app.seeder import seed

# Auto-create tables
Base.metadata.create_all(bind=engine)

# Seed on startup
with SessionLocal() as db:
    seed(db)

app = FastAPI(title="Starter API", version="1.0.0", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=86400,
)


# Global exception → ApiResponse format
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        content={"success": False, "message": exc.detail},
        status_code=exc.status_code,
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        content={"success": False, "message": str(exc)},
        status_code=400,
    )


@app.exception_handler(KeyError)
async def key_error_handler(request: Request, exc: KeyError):
    return JSONResponse(
        content={"success": False, "message": str(exc).strip("'")},
        status_code=404,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        content={"success": False, "message": "Internal server error"},
        status_code=500,
    )


# Serve uploaded photos
os.makedirs(settings.storage_path, exist_ok=True)
app.mount("/storage/photos", StaticFiles(directory=settings.storage_path), name="photos")

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(permissions.router)
app.include_router(lookup.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.app_port, reload=True)
