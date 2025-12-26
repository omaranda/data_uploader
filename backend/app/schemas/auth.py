from __future__ import annotations
from typing import Optional

"""Authentication schemas."""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    """User info in auth responses."""

    id: int
    username: str
    email: EmailStr
    full_name: Optional[str]
    role: str
    company_id: int
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires
    user: Optional[UserResponse] = None  # User information


class TokenRefresh(BaseModel):
    """Token refresh request schema."""

    refresh_token: str
