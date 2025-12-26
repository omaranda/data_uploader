from __future__ import annotations
from typing import Optional

"""User schemas."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    full_name: Optional[str] = None
    role: str = Field(default="user", pattern="^(admin|user)$")
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a user."""

    company_id: int
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(admin|user)$")
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)


class UserInDB(UserBase):
    """User schema with password hash (internal use)."""

    id: int
    company_id: int
    password_hash: str
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(UserBase):
    """Schema for user in list responses."""

    id: int
    company_id: int
    last_login: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
