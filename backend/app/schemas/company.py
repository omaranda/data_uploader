from __future__ import annotations
from typing import Optional

"""Company schemas."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class CompanyBase(BaseModel):
    """Base company schema."""

    company_name: str = Field(..., min_length=1, max_length=255)
    company_code: str = Field(..., min_length=1, max_length=50)
    contact_email: Optional[EmailStr] = None
    is_active: bool = True


class CompanyCreate(CompanyBase):
    """Schema for creating a company."""

    pass


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""

    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    company_code: Optional[str] = Field(None, min_length=1, max_length=50)
    contact_email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class CompanyResponse(CompanyBase):
    """Schema for company responses."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
