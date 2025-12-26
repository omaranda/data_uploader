# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

"""Utilities for company-scoped data access."""

from __future__ import annotations

from typing import Any, Optional
from sqlalchemy.orm import Session

from app.models import Company, Project, User, Cycle, SyncSession


def get_company_filter(company_id: int) -> dict[str, Any]:
    """
    Get filter dictionary for company-scoped queries.

    Args:
        company_id: The company ID to filter by

    Returns:
        Dictionary with company_id filter
    """
    return {"company_id": company_id}


def verify_company_access(
    db: Session,
    user_company_id: int,
    resource_model: type,
    resource_id: int,
    company_field: str = "company_id"
) -> bool:
    """
    Verify that a user has access to a resource based on company.

    Args:
        db: Database session
        user_company_id: The user's company ID
        resource_model: The SQLAlchemy model class
        resource_id: The resource ID to check
        company_field: The field name for company_id (default: "company_id")

    Returns:
        True if user has access, False otherwise
    """
    resource = db.query(resource_model).filter(
        resource_model.id == resource_id
    ).first()

    if not resource:
        return False

    # Get the company_id from the resource
    resource_company_id = getattr(resource, company_field, None)

    return resource_company_id == user_company_id


def verify_project_access(
    db: Session,
    user_company_id: int,
    project_id: int
) -> bool:
    """
    Verify that a user has access to a specific project.

    Args:
        db: Database session
        user_company_id: The user's company ID
        project_id: The project ID to check

    Returns:
        True if user has access, False otherwise
    """
    return verify_company_access(db, user_company_id, Project, project_id)


def verify_user_access(
    db: Session,
    user_company_id: int,
    target_user_id: int
) -> bool:
    """
    Verify that a user can access another user (same company).

    Args:
        db: Database session
        user_company_id: The requesting user's company ID
        target_user_id: The target user ID to check

    Returns:
        True if users are in same company, False otherwise
    """
    return verify_company_access(db, user_company_id, User, target_user_id)


def get_project_company_id(db: Session, project_id: int) -> Optional[int]:
    """
    Get the company_id for a given project.

    Args:
        db: Database session
        project_id: The project ID

    Returns:
        The company_id or None if project not found
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    return project.company_id if project else None


def verify_cycle_access(
    db: Session,
    user_company_id: int,
    cycle_id: int
) -> bool:
    """
    Verify that a user has access to a cycle (via project).

    Args:
        db: Database session
        user_company_id: The user's company ID
        cycle_id: The cycle ID to check

    Returns:
        True if user has access, False otherwise
    """
    cycle = db.query(Cycle).filter(Cycle.id == cycle_id).first()
    if not cycle:
        return False

    project_company_id = get_project_company_id(db, cycle.project_id)
    return project_company_id == user_company_id


def verify_session_access(
    db: Session,
    user_company_id: int,
    session_id: int
) -> bool:
    """
    Verify that a user has access to a sync session (via project).

    Args:
        db: Database session
        user_company_id: The user's company ID
        session_id: The session ID to check

    Returns:
        True if user has access, False otherwise
    """
    session = db.query(SyncSession).filter(SyncSession.id == session_id).first()
    if not session:
        return False

    project_company_id = get_project_company_id(db, session.project_id)
    return project_company_id == user_company_id
