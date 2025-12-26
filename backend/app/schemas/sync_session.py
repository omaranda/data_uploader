"""Sync session schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SyncSessionCreate(BaseModel):
    """Schema for creating a new sync session."""

    project_id: int = Field(..., description="Project ID")
    cycle_id: Optional[int] = Field(None, description="Cycle ID (optional)")
    local_directory: str = Field(..., description="Local directory path")
    s3_prefix: str = Field(..., max_length=500, description="S3 prefix for upload")
    aws_profile: str = Field(default="default", max_length=100, description="AWS profile name")
    max_workers: int = Field(default=15, ge=1, le=50, description="Number of concurrent workers")
    times_to_retry: int = Field(default=3, ge=0, le=10, description="Number of retry attempts")
    use_find: bool = Field(default=True, description="Use find command for file discovery")


class SyncSessionUpdate(BaseModel):
    """Schema for updating a sync session."""

    status: Optional[str] = Field(
        None,
        pattern="^(pending|in_progress|completed|failed|incomplete)$"
    )
    total_files: Optional[int] = Field(None, ge=0)
    files_uploaded: Optional[int] = Field(None, ge=0)
    files_failed: Optional[int] = Field(None, ge=0)
    files_skipped: Optional[int] = Field(None, ge=0)
    total_size_bytes: Optional[int] = Field(None, ge=0)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SyncSessionResponse(BaseModel):
    """Schema for sync session responses."""

    id: int
    project_id: int
    cycle_id: Optional[int]
    user_id: Optional[int]
    local_directory: str
    s3_prefix: str
    aws_profile: str
    max_workers: int
    times_to_retry: int
    use_find: bool
    status: str
    total_files: int
    files_uploaded: int
    files_failed: int
    files_skipped: int
    total_size_bytes: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class SyncSessionStats(BaseModel):
    """Schema for sync session statistics."""

    total_sessions: int
    active_sessions: int
    completed_sessions: int
    failed_sessions: int
    total_files_uploaded: int
    total_bytes_uploaded: int
