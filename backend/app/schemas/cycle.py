# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

"""Cycle schemas."""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field


class CycleBase(BaseModel):
    """Base cycle schema."""

    cycle_name: str = Field(..., min_length=1, max_length=50)
    cycle_number: int = Field(..., ge=1)
    s3_prefix: str = Field(..., min_length=1, max_length=100)
    status: str = Field(
        default="pending",
        pattern="^(pending|in_progress|completed|incomplete)$"
    )
    description: Optional[str] = None
    cycle_metadata: Optional[dict[str, Any]] = None


class CycleCreate(CycleBase):
    """Schema for creating a cycle."""

    project_id: int


class CycleUpdate(BaseModel):
    """Schema for updating a cycle."""

    cycle_name: Optional[str] = Field(None, min_length=1, max_length=50)
    status: Optional[str] = Field(
        None,
        pattern="^(pending|in_progress|completed|incomplete)$"
    )
    description: Optional[str] = None
    cycle_metadata: Optional[dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class CycleResponse(CycleBase):
    """Schema for cycle responses."""

    id: int
    project_id: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
