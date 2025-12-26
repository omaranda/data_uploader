# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations
from typing import Optional

"""Project schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base project schema."""

    project_name: str = Field(..., min_length=1, max_length=255)
    bucket_name: str = Field(..., min_length=1, max_length=255)
    aws_region: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    is_active: bool = True


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""

    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""

    project_name: Optional[str] = Field(None, min_length=1, max_length=255)
    bucket_name: Optional[str] = Field(None, min_length=1, max_length=255)
    aws_region: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProjectResponse(ProjectBase):
    """Schema for project responses."""

    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
