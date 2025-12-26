"""Cycles router - CRUD operations for cycles."""

from __future__ import annotations

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models import User, Cycle, Project
from app.schemas.cycle import CycleCreate, CycleUpdate, CycleResponse

router = APIRouter(prefix="/api/cycles", tags=["Cycles"])


@router.get("/", response_model=List[CycleResponse])
async def list_cycles(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    List cycles with optional filters.

    Args:
        project_id: Filter by project ID (optional)
        status: Filter by status (optional)
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        List of cycles
    """
    # Start with cycles from user's company projects
    query = db.query(Cycle).join(Project).filter(
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

        query = query.filter(Cycle.project_id == project_id)

    if status:
        query = query.filter(Cycle.status == status)

    cycles = query.order_by(Cycle.project_id, Cycle.cycle_number).offset(skip).limit(limit).all()
    return cycles


@router.get("/{cycle_id}", response_model=CycleResponse)
async def get_cycle(
    cycle_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get a specific cycle by ID.

    Args:
        cycle_id: Cycle ID

    Returns:
        Cycle details

    Raises:
        404: Cycle not found
        403: Access denied
    """
    cycle = db.query(Cycle).join(Project).filter(
        Cycle.id == cycle_id
    ).first()

    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cycle with id {cycle_id} not found"
        )

    # Verify access via project
    project = db.query(Project).filter(Project.id == cycle.project_id).first()
    if project.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return cycle


@router.post("/", response_model=CycleResponse, status_code=status.HTTP_201_CREATED)
async def create_cycle(
    cycle_data: CycleCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Create a new cycle.

    Args:
        cycle_data: Cycle creation data

    Returns:
        Created cycle

    Raises:
        404: Project not found
        403: Access denied
        400: Cycle name or number already exists for this project
    """
    # Verify project exists and user has access
    project = db.query(Project).filter(
        Project.id == cycle_data.project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {cycle_data.project_id} not found"
        )

    if project.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Check for duplicate cycle name
    existing_name = db.query(Cycle).filter(
        Cycle.project_id == cycle_data.project_id,
        Cycle.cycle_name == cycle_data.cycle_name
    ).first()

    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cycle with name '{cycle_data.cycle_name}' already exists for this project"
        )

    # Check for duplicate cycle number
    existing_number = db.query(Cycle).filter(
        Cycle.project_id == cycle_data.project_id,
        Cycle.cycle_number == cycle_data.cycle_number
    ).first()

    if existing_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cycle with number {cycle_data.cycle_number} already exists for this project"
        )

    # Create cycle
    cycle = Cycle(
        project_id=cycle_data.project_id,
        cycle_name=cycle_data.cycle_name,
        cycle_number=cycle_data.cycle_number,
        s3_prefix=cycle_data.s3_prefix,
        status=cycle_data.status,
        description=cycle_data.description,
        cycle_metadata=cycle_data.cycle_metadata
    )

    db.add(cycle)
    db.commit()
    db.refresh(cycle)

    return cycle


@router.put("/{cycle_id}", response_model=CycleResponse)
async def update_cycle(
    cycle_id: int,
    cycle_data: CycleUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Update an existing cycle.

    Args:
        cycle_id: Cycle ID
        cycle_data: Cycle update data

    Returns:
        Updated cycle

    Raises:
        404: Cycle not found
        403: Access denied
        400: Cycle name already exists
    """
    cycle = db.query(Cycle).filter(Cycle.id == cycle_id).first()

    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cycle with id {cycle_id} not found"
        )

    # Verify access via project
    project = db.query(Project).filter(Project.id == cycle.project_id).first()
    if project.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Check for name conflict if updating name
    if cycle_data.cycle_name and cycle_data.cycle_name != cycle.cycle_name:
        existing = db.query(Cycle).filter(
            Cycle.project_id == cycle.project_id,
            Cycle.cycle_name == cycle_data.cycle_name,
            Cycle.id != cycle_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cycle with name '{cycle_data.cycle_name}' already exists for this project"
            )

    # Update fields
    update_data = cycle_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cycle, field, value)

    db.commit()
    db.refresh(cycle)

    return cycle


@router.delete("/{cycle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cycle(
    cycle_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Delete a cycle.

    This will set cycle_id to NULL in associated sessions.

    Args:
        cycle_id: Cycle ID

    Raises:
        404: Cycle not found
        403: Access denied
    """
    cycle = db.query(Cycle).filter(Cycle.id == cycle_id).first()

    if not cycle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cycle with id {cycle_id} not found"
        )

    # Verify access via project
    project = db.query(Project).filter(Project.id == cycle.project_id).first()
    if project.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    db.delete(cycle)
    db.commit()

    return None
