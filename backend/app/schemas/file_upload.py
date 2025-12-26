from __future__ import annotations
from typing import Optional

"""File upload schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """Schema for file upload responses."""

    id: int
    session_id: int
    file_path: str
    s3_key: str
    file_size: Optional[int]
    checksum: Optional[str]
    status: str = Field(
        ...,
        pattern="^(pending|uploading|completed|failed|skipped)$"
    )
    error_message: Optional[str]
    uploaded_at: Optional[datetime]
    is_duplicate: bool
    created_at: datetime

    class Config:
        from_attributes = True
