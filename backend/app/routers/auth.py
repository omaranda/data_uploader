# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

"""Authentication router."""

from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models import User
from app.schemas.auth import LoginRequest, Token, TokenRefresh, UserResponse
from app.utils.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type
)
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Authenticate user and return JWT tokens.

    Args:
        login_data: Username and password
        db: Database session

    Returns:
        Access token, refresh token, and expiration info

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by username
    user = db.query(User).filter(User.username == login_data.username).first()

    # Verify user exists and password is correct
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Update last login timestamp
    user.last_login = datetime.utcnow()
    db.commit()

    # Create JWT tokens
    token_data = {
        "user_id": user.id,
        "company_id": user.company_id,
        "role": user.role
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            company_id=user.company_id,
            is_active=user.is_active
        )
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: TokenRefresh,
    db: Annotated[Session, Depends(get_db)]
):
    """
    Refresh access token using refresh token.

    Args:
        refresh_data: Refresh token
        db: Database session

    Returns:
        New access token and refresh token

    Raises:
        HTTPException: If refresh token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(refresh_data.refresh_token)

        # Verify it's a refresh token
        if not verify_token_type(payload, "refresh"):
            raise credentials_exception

        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception

    except Exception:
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception

    # Create new tokens
    token_data = {
        "user_id": user.id,
        "company_id": user.company_id,
        "role": user.role
    }

    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        company_id=current_user.company_id,
        is_active=current_user.is_active
    )
