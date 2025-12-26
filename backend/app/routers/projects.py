# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

"""Projects router - CRUD operations for projects."""

from __future__ import annotations

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user, get_company_filter
from app.models import User, Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
):
    """
    List all projects for the current user's company.

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        is_active: Filter by active status (optional)

    Returns:
        List of projects
    """
    query = db.query(Project).filter(Project.company_id == current_user.company_id)

    if is_active is not None:
        query = query.filter(Project.is_active == is_active)

    projects = query.offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get a specific project by ID.

    Args:
        project_id: Project ID

    Returns:
        Project details

    Raises:
        404: Project not found
        403: Access denied (different company)
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )

    # Verify user has access (same company)
    if project.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return project


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Create a new project.

    The project will be associated with the current user's company.

    Args:
        project_data: Project creation data

    Returns:
        Created project

    Raises:
        400: Project name already exists
    """
    # Check if project name already exists
    existing = db.query(Project).filter(
        Project.project_name == project_data.project_name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Project with name '{project_data.project_name}' already exists"
        )

    # Create project for current user's company
    project = Project(
        company_id=current_user.company_id,
        project_name=project_data.project_name,
        bucket_name=project_data.bucket_name,
        aws_region=project_data.aws_region,
        description=project_data.description,
        is_active=project_data.is_active
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Update an existing project.

    Args:
        project_id: Project ID
        project_data: Project update data

    Returns:
        Updated project

    Raises:
        404: Project not found
        403: Access denied
        400: Project name already exists
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )

    # Verify access
    if project.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Check for name conflict if updating name
    if project_data.project_name and project_data.project_name != project.project_name:
        existing = db.query(Project).filter(
            Project.project_name == project_data.project_name,
            Project.id != project_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project with name '{project_data.project_name}' already exists"
            )

    # Update fields
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)

    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Delete a project.

    This will cascade delete all associated cycles and sessions.

    Args:
        project_id: Project ID

    Raises:
        404: Project not found
        403: Access denied
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )

    # Verify access
    if project.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    db.delete(project)
    db.commit()

    return None
