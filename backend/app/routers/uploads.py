# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

"""Uploads router - start and monitor background upload jobs."""

from __future__ import annotations

from typing import Annotated, Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import boto3
from botocore.exceptions import ClientError

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models import User, SyncSession, Project
from app.services.queue import enqueue_upload_job, get_job_status
from app.utils.company_scoped import verify_project_access
from app.config import settings

router = APIRouter(prefix="/api/uploads", tags=["Uploads"])


class UploadStartRequest(BaseModel):
    """Request schema for starting an upload job."""

    session_id: int


class UploadStartResponse(BaseModel):
    """Response schema for upload job start."""

    job_id: str
    session_id: int
    status: str
    message: str


class JobStatusResponse(BaseModel):
    """Response schema for job status."""

    job_id: str
    status: str
    session_id: Optional[int]
    created_at: Optional[str]
    started_at: Optional[str]
    ended_at: Optional[str]
    result: Optional[Dict[str, Any]]
    error: Optional[str]


@router.post("/start", response_model=UploadStartResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_upload(
    request: UploadStartRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Start a background upload job for a session.

    Args:
        request: Upload start request with session_id
        db: Database session
        current_user: Current authenticated user

    Returns:
        Upload job information

    Raises:
        404: Session not found
        403: Access denied (different company)
        400: Invalid session state
    """
    # Get session from database
    session = db.query(SyncSession).filter(
        SyncSession.id == request.session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {request.session_id} not found"
        )

    # Verify access via project's company
    project = db.query(Project).filter(Project.id == session.project_id).first()
    if not project or project.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Check session is in pending status
    if session.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session must be in 'pending' status to start upload. Current status: {session.status}"
        )

    # Build upload configuration
    config = {
        'local_directory': session.local_directory,
        'bucket_name': project.bucket_name,
        's3_prefix': session.s3_prefix,
        'aws_region': project.aws_region,
        'aws_profile': session.aws_profile,
        'max_workers': session.max_workers,
        'times_to_retry': session.times_to_retry,
        'use_find': session.use_find
    }

    # Enqueue the upload job
    job_id = enqueue_upload_job(
        session_id=session.id,
        config=config
    )

    # Update session status to queued
    session.status = 'in_progress'
    db.commit()

    return UploadStartResponse(
        job_id=job_id,
        session_id=session.id,
        status='queued',
        message=f'Upload job {job_id} has been queued'
    )


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_upload_status(
    job_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get the status of an upload job.

    Args:
        job_id: The job ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Job status information

    Raises:
        404: Job not found
    """
    job_status = get_job_status(job_id)

    if job_status.get('status') == 'not_found':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )

    # Extract session_id from result if available
    session_id = None
    if job_status.get('result') and isinstance(job_status['result'], dict):
        session_id = job_status['result'].get('session_id')

    return JobStatusResponse(
        job_id=job_id,
        status=job_status.get('status', 'unknown'),
        session_id=session_id,
        created_at=job_status.get('created_at'),
        started_at=job_status.get('started_at'),
        ended_at=job_status.get('ended_at'),
        result=job_status.get('result'),
        error=job_status.get('exc_info')
    )


class PresignedUrlRequest(BaseModel):
    """Request schema for generating presigned URLs."""

    session_id: int
    file_key: str  # Relative path from s3_prefix (e.g., "folder/file.txt")


class PresignedUrlResponse(BaseModel):
    """Response schema for presigned URL."""

    presigned_url: str
    file_key: str
    full_s3_key: str  # Complete S3 key including prefix
    expires_in: int  # Seconds until expiration


@router.post("/presigned-url", response_model=PresignedUrlResponse)
async def generate_presigned_url(
    request: PresignedUrlRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Generate a presigned URL for direct browser upload to S3.

    Args:
        request: Presigned URL request with session_id and file_key
        db: Database session
        current_user: Current authenticated user

    Returns:
        Presigned URL and metadata

    Raises:
        404: Session not found
        403: Access denied
        500: AWS error
    """
    # Get session from database
    session = db.query(SyncSession).filter(
        SyncSession.id == request.session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {request.session_id} not found"
        )

    # Verify access via project's company
    project = db.query(Project).filter(Project.id == session.project_id).first()
    if not project or project.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Build full S3 key (prefix + file_key)
    full_s3_key = f"{session.s3_prefix.rstrip('/')}/{request.file_key.lstrip('/')}"

    # Create S3 client with Signature Version 4 for CORS compatibility
    try:
        from botocore.config import Config

        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
            region_name=settings.AWS_DEFAULT_REGION,
            config=Config(signature_version='s3v4')
        )

        # Generate presigned URL (valid for 1 hour)
        # Note: ServerSideEncryption is handled automatically by bucket default encryption
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': project.bucket_name,
                'Key': full_s3_key
            },
            ExpiresIn=3600  # 1 hour
        )

        return PresignedUrlResponse(
            presigned_url=presigned_url,
            file_key=request.file_key,
            full_s3_key=full_s3_key,
            expires_in=3600
        )

    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AWS error: {str(e)}"
        )
