"""Sessions router - CRUD operations for sync sessions."""

from __future__ import annotations

from typing import Annotated, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models import User, SyncSession, Project
from app.schemas.sync_session import SyncSessionCreate, SyncSessionUpdate, SyncSessionResponse, SyncSessionStats
from app.utils.company_scoped import verify_project_access

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.get("/", response_model=List[SyncSessionResponse])
async def list_sessions(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
    cycle_id: Optional[int] = None,
    status: Optional[str] = None
):
    """
    List all sync sessions for the current user's company.

    Sessions are company-scoped via project relationship.

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        project_id: Filter by project ID (optional)
        cycle_id: Filter by cycle ID (optional)
        status: Filter by status (optional)

    Returns:
        List of sync sessions
    """
    # Start with sessions from user's company projects
    query = db.query(SyncSession).join(Project).filter(
        Project.company_id == current_user.company_id
    )

    if project_id is not None:
        # Verify project belongs to user's company
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.company_id == current_user.company_id
        ).first()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {project_id} not found"
            )

        query = query.filter(SyncSession.project_id == project_id)

    if cycle_id is not None:
        query = query.filter(SyncSession.cycle_id == cycle_id)

    if status is not None:
        query = query.filter(SyncSession.status == status)

    sessions = query.order_by(SyncSession.created_at.desc()).offset(skip).limit(limit).all()
    return sessions


@router.get("/stats", response_model=SyncSessionStats)
async def get_session_stats(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    project_id: Optional[int] = None
):
    """
    Get statistics for sync sessions.

    Args:
        project_id: Filter stats by project ID (optional)

    Returns:
        Session statistics
    """
    # Base query for user's company sessions
    query = db.query(SyncSession).join(Project).filter(
        Project.company_id == current_user.company_id
    )

    if project_id is not None:
        # Verify project belongs to user's company
        if not verify_project_access(db, current_user.company_id, project_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {project_id} not found"
            )
        query = query.filter(SyncSession.project_id == project_id)

    # Calculate statistics
    total_sessions = query.count()
    active_sessions = query.filter(SyncSession.status == "in_progress").count()
    completed_sessions = query.filter(SyncSession.status == "completed").count()
    failed_sessions = query.filter(SyncSession.status == "failed").count()

    # Aggregate file and byte counts
    aggregates = query.with_entities(
        func.sum(SyncSession.files_uploaded).label("total_files"),
        func.sum(SyncSession.total_size_bytes).label("total_bytes")
    ).first()

    return SyncSessionStats(
        total_sessions=total_sessions,
        active_sessions=active_sessions,
        completed_sessions=completed_sessions,
        failed_sessions=failed_sessions,
        total_files_uploaded=aggregates.total_files or 0,
        total_bytes_uploaded=aggregates.total_bytes or 0
    )


@router.get("/{session_id}", response_model=SyncSessionResponse)
async def get_session(
    session_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get a specific sync session by ID.

    Args:
        session_id: Session ID

    Returns:
        Session details

    Raises:
        404: Session not found
        403: Access denied (different company)
    """
    session = db.query(SyncSession).filter(SyncSession.id == session_id).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found"
        )

    # Verify access via project's company
    project = db.query(Project).filter(Project.id == session.project_id).first()
    if not project or project.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return session


@router.post("/", response_model=SyncSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SyncSessionCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Create a new sync session.

    Args:
        session_data: Session creation data

    Returns:
        Created session

    Raises:
        404: Project or cycle not found
        403: Access denied (different company)
    """
    # Verify project belongs to user's company
    project = db.query(Project).filter(
        Project.id == session_data.project_id,
        Project.company_id == current_user.company_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {session_data.project_id} not found"
        )

    # Create session
    session = SyncSession(
        project_id=session_data.project_id,
        cycle_id=session_data.cycle_id,
        user_id=current_user.id,
        local_directory=session_data.local_directory,
        s3_prefix=session_data.s3_prefix,
        aws_profile=session_data.aws_profile,
        max_workers=session_data.max_workers,
        times_to_retry=session_data.times_to_retry,
        use_find=session_data.use_find,
        status="pending",
        started_at=datetime.utcnow()
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


@router.put("/{session_id}", response_model=SyncSessionResponse)
async def update_session(
    session_id: int,
    session_data: SyncSessionUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Update an existing sync session.

    Typically used by background workers to update progress.

    Args:
        session_id: Session ID
        session_data: Session update data

    Returns:
        Updated session

    Raises:
        404: Session not found
        403: Access denied
    """
    session = db.query(SyncSession).filter(SyncSession.id == session_id).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found"
        )

    # Verify access via project's company
    project = db.query(Project).filter(Project.id == session.project_id).first()
    if not project or project.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Update fields
    update_data = session_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)

    db.commit()
    db.refresh(session)

    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Delete a sync session.

    Args:
        session_id: Session ID

    Raises:
        404: Session not found
        403: Access denied
        400: Cannot delete active session
    """
    session = db.query(SyncSession).filter(SyncSession.id == session_id).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found"
        )

    # Verify access via project's company
    project = db.query(Project).filter(Project.id == session.project_id).first()
    if not project or project.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Prevent deletion of active sessions
    if session.status == "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete an active session"
        )

    db.delete(session)
    db.commit()

    return None
