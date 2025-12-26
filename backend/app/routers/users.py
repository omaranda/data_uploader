# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

"""Users router - CRUD operations for users."""

from __future__ import annotations

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user, get_current_admin
from app.models import User
from app.schemas.user import UserCreate, UserUpdate, UserListResponse
from app.utils.security import hash_password

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/", response_model=List[UserListResponse])
async def list_users(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
):
    """
    List all users in the current user's company.

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        is_active: Filter by active status (optional)

    Returns:
        List of users
    """
    query = db.query(User).filter(User.company_id == current_user.company_id)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserListResponse)
async def get_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get a specific user by ID.

    Args:
        user_id: User ID

    Returns:
        User details

    Raises:
        404: User not found
        403: Access denied (different company)
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    # Verify user has access (same company)
    if user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return user


@router.post("/", response_model=UserListResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)]
):
    """
    Create a new user (admin only).

    The user will be created in the specified company.
    Only admins can create users.

    Args:
        user_data: User creation data

    Returns:
        Created user

    Raises:
        400: Username or email already exists
        403: Not admin or trying to create user in different company
    """
    # Verify admin is creating user in their own company
    if user_data.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create users in other companies"
        )

    # Check if username already exists
    existing_username = db.query(User).filter(
        User.username == user_data.username
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user_data.username}' already exists"
        )

    # Check if email already exists
    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user_data.email}' already exists"
        )

    # Create user
    user = User(
        company_id=user_data.company_id,
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=user_data.is_active
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.put("/{user_id}", response_model=UserListResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)]
):
    """
    Update an existing user (admin only).

    Args:
        user_id: User ID
        user_data: User update data

    Returns:
        Updated user

    Raises:
        404: User not found
        403: Access denied
        400: Email already exists
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    # Verify access (same company)
    if user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Check for email conflict if updating email
    if user_data.email and user_data.email != user.email:
        existing = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{user_data.email}' already exists"
            )

    # Update fields
    update_data = user_data.model_dump(exclude_unset=True, exclude={'password'})
    for field, value in update_data.items():
        setattr(user, field, value)

    # Update password if provided
    if user_data.password:
        user.password_hash = hash_password(user_data.password)

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)]
):
    """
    Delete a user (admin only).

    Args:
        user_id: User ID

    Raises:
        404: User not found
        403: Access denied
        400: Cannot delete yourself
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    # Verify access
    if user.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Prevent self-deletion
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )

    db.delete(user)
    db.commit()

    return None
