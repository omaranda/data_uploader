# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

"""Companies router - CRUD operations for companies (admin only)."""

from __future__ import annotations

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_admin
from app.models import User, Company
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse

router = APIRouter(prefix="/api/companies", tags=["Companies"])


@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)],
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
):
    """
    List all companies (admin only).

    Admins can only see their own company.

    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        is_active: Filter by active status (optional)

    Returns:
        List of companies
    """
    # Admins can only see their own company
    query = db.query(Company).filter(Company.id == current_user.company_id)

    if is_active is not None:
        query = query.filter(Company.is_active == is_active)

    companies = query.offset(skip).limit(limit).all()
    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)]
):
    """
    Get a specific company by ID (admin only).

    Admins can only access their own company.

    Args:
        company_id: Company ID

    Returns:
        Company details

    Raises:
        404: Company not found
        403: Access denied
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} not found"
        )

    # Verify access (own company only)
    if company.id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return company


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_admin)]
):
    """
    Update company details (admin only).

    Admins can only update their own company.

    Args:
        company_id: Company ID
        company_data: Company update data

    Returns:
        Updated company

    Raises:
        404: Company not found
        403: Access denied
        400: Company name or code already exists
    """
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with id {company_id} not found"
        )

    # Verify access (own company only)
    if company.id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # Check for name conflict if updating name
    if company_data.company_name and company_data.company_name != company.company_name:
        existing = db.query(Company).filter(
            Company.company_name == company_data.company_name,
            Company.id != company_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Company with name '{company_data.company_name}' already exists"
            )

    # Check for code conflict if updating code
    if company_data.company_code and company_data.company_code != company.company_code:
        existing = db.query(Company).filter(
            Company.company_code == company_data.company_code,
            Company.id != company_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Company with code '{company_data.company_code}' already exists"
            )

    # Update fields
    update_data = company_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)

    return company
