# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

"""FastAPI application entry point."""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging

from app.config import settings
from app.routers import auth, projects, users, companies, cycles, sessions, uploads
from app.models import Base
from app.database import engine

logger = logging.getLogger(__name__)

# Create database tables (if not exists)
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Data Uploader API",
    description="Multi-tenant file upload system with FastAPI backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log and return validation errors."""
    logger.error(f"Validation error for {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(cycles.router)
app.include_router(sessions.router)
app.include_router(uploads.router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "data-uploader-api",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Data Uploader API",
        "docs": "/docs",
        "health": "/health"
    }
