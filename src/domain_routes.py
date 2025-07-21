"""
Domain management endpoints for authenticated users.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from src.database import get_db
from src.models import UserDomain, DomainCheck as DomainCheckModel, User as UserModel
from src.schemas import (
    UserDomainCreateRequest, UserDomainUpdateRequest, UserDomainResponse,
    AuthenticatedDomainCheckRequest, DomainCheckResponse, 
    DomainCheckHistoryResponse, DomainStatsResponse
)
from src.auth_dependencies import get_current_user, User
from src.dns_utils import check_all_dns_records
from src.email_service import get_email_service
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/domains", tags=["Domain Management"])


@router.get("/", response_model=List[UserDomainResponse])
async def get_user_domains(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all domains managed by the current user.
    
    Requires valid JWT token.
    """
    domains = db.query(UserDomain).filter(UserDomain.user_id == current_user.id).order_by(UserDomain.created_at.desc()).all()
    return domains


@router.post("/", response_model=UserDomainResponse, status_code=status.HTTP_201_CREATED)
async def add_user_domain(
    request: UserDomainCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new domain to user's managed domains.
    
    - **domain**: Domain name to add (e.g., "example.com")
    - **display_name**: Optional friendly name for the domain
    - **auto_check_enabled**: Enable automatic periodic checks
    - **check_frequency**: Frequency for auto checks ("weekly" or "monthly")
    
    Requires valid JWT token.
    """
    # Check if domain already exists for this user
    existing = db.query(UserDomain).filter(
        and_(UserDomain.user_id == current_user.id, UserDomain.domain == request.domain)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Domain already exists in your account"
        )
    
    # Create new domain
    domain = UserDomain(
        user_id=current_user.id,
        domain=request.domain,
        display_name=request.display_name,
        auto_check_enabled=request.auto_check_enabled,
        check_frequency=request.check_frequency
    )
    
    db.add(domain)
    db.commit()
    db.refresh(domain)
    
    return domain


@router.get("/{domain_id}", response_model=UserDomainResponse)
async def get_user_domain(
    domain_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific managed domain.
    
    Requires valid JWT token and domain ownership.
    """
    domain = db.query(UserDomain).filter(
        and_(UserDomain.id == domain_id, UserDomain.user_id == current_user.id)
    ).first()
    
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    
    return domain


@router.put("/{domain_id}", response_model=UserDomainResponse)
async def update_user_domain(
    domain_id: int,
    request: UserDomainUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a managed domain's settings.
    
    - **display_name**: Updated friendly name
    - **auto_check_enabled**: Enable/disable automatic checks
    - **check_frequency**: Update check frequency
    
    Requires valid JWT token and domain ownership.
    """
    domain = db.query(UserDomain).filter(
        and_(UserDomain.id == domain_id, UserDomain.user_id == current_user.id)
    ).first()
    
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    
    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(domain, field, value)
    
    domain.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(domain)
    
    return domain


@router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_domain(
    domain_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a domain from managed domains.
    
    This will also delete all associated check history.
    Requires valid JWT token and domain ownership.
    """
    domain = db.query(UserDomain).filter(
        and_(UserDomain.id == domain_id, UserDomain.user_id == current_user.id)
    ).first()
    
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    
    db.delete(domain)
    db.commit()


@router.post("/{domain_id}/check", response_model=DomainCheckResponse)
async def run_domain_check(
    domain_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Run a security check on a managed domain.
    
    Performs comprehensive DNS security analysis and saves results to history.
    Requires valid JWT token and domain ownership.
    """
    domain = db.query(UserDomain).filter(
        and_(UserDomain.id == domain_id, UserDomain.user_id == current_user.id)
    ).first()
    
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    
    try:
        # Run DNS checks
        results = await check_all_dns_records(domain.domain)
        
        # Create domain check record
        domain_check = DomainCheckModel(
            email=current_user.email,
            domain=domain.domain,
            user_id=current_user.id,
            user_domain_id=domain.id,
            mx_record=results.get("mx"),
            spf_record=results.get("spf"),
            dkim_record=results.get("dkim"),
            dmarc_record=results.get("dmarc"),
            score=results.get("score"),
            grade=results.get("grade"),
            issues=results.get("issues", []),
            recommendations=results.get("recommendations", []),
            security_summary=results.get("security_summary")
        )
        
        db.add(domain_check)
        
        # Update domain's last check time
        domain.last_auto_check = datetime.utcnow()
        domain.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(domain_check)
        
        return DomainCheckResponse(
            id=domain_check.id,
            email=domain_check.email,
            domain=domain_check.domain,
            mx_record=domain_check.mx_record,
            spf_record=domain_check.spf_record,
            dkim_record=domain_check.dkim_record,
            dmarc_record=domain_check.dmarc_record,
            score=domain_check.score,
            grade=domain_check.grade,
            issues=domain_check.issues,
            recommendations=domain_check.recommendations,
            security_summary=domain_check.security_summary,
            opt_in_marketing=False,
            created_at=domain_check.created_at,
            updated_at=domain_check.updated_at
        )
        
    except Exception as e:
        logger.error(f"Domain check failed for {domain.domain}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Domain check failed. Please try again."
        )


@router.get("/{domain_id}/history", response_model=DomainCheckHistoryResponse)
async def get_domain_check_history(
    domain_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get check history for a specific domain.
    
    - **page**: Page number (starts at 1)
    - **per_page**: Number of results per page (1-100)
    
    Requires valid JWT token and domain ownership.
    """
    domain = db.query(UserDomain).filter(
        and_(UserDomain.id == domain_id, UserDomain.user_id == current_user.id)
    ).first()
    
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain not found"
        )
    
    # Get paginated check history
    offset = (page - 1) * per_page
    checks_query = db.query(DomainCheckModel).filter(
        DomainCheckModel.user_domain_id == domain_id
    ).order_by(DomainCheckModel.created_at.desc())
    
    total_count = checks_query.count()
    checks = checks_query.offset(offset).limit(per_page).all()
    
    # Convert to response format
    check_responses = []
    for check in checks:
        check_responses.append(DomainCheckResponse(
            id=check.id,
            email=check.email,
            domain=check.domain,
            mx_record=check.mx_record,
            spf_record=check.spf_record,
            dkim_record=check.dkim_record,
            dmarc_record=check.dmarc_record,
            score=check.score,
            grade=check.grade,
            issues=check.issues,
            recommendations=check.recommendations,
            security_summary=check.security_summary,
            opt_in_marketing=False,
            created_at=check.created_at,
            updated_at=check.updated_at
        ))
    
    return DomainCheckHistoryResponse(
        checks=check_responses,
        total_count=total_count,
        page=page,
        per_page=per_page,
        has_next=(offset + per_page) < total_count,
        has_prev=page > 1
    )


@router.get("/stats", response_model=DomainStatsResponse)
async def get_domain_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get domain statistics for the current user.
    
    Provides overview of managed domains, check counts, and recent activity.
    Requires valid JWT token.
    """
    # Get basic counts
    total_domains = db.query(UserDomain).filter(UserDomain.user_id == current_user.id).count()
    total_checks = db.query(DomainCheckModel).filter(DomainCheckModel.user_id == current_user.id).count()
    
    # Get average score
    avg_score_result = db.query(func.avg(DomainCheckModel.score)).filter(
        and_(DomainCheckModel.user_id == current_user.id, DomainCheckModel.score.isnot(None))
    ).scalar()
    
    # Get domains by grade
    grade_counts = db.query(
        DomainCheckModel.grade, func.count(DomainCheckModel.grade)
    ).filter(
        and_(DomainCheckModel.user_id == current_user.id, DomainCheckModel.grade.isnot(None))
    ).group_by(DomainCheckModel.grade).all()
    
    domains_by_grade = {grade: count for grade, count in grade_counts}
    
    # Get recent checks (last 5)
    recent_checks = db.query(DomainCheckModel).filter(
        DomainCheckModel.user_id == current_user.id
    ).order_by(DomainCheckModel.created_at.desc()).limit(5).all()
    
    recent_check_responses = []
    for check in recent_checks:
        recent_check_responses.append(DomainCheckResponse(
            id=check.id,
            email=check.email,
            domain=check.domain,
            mx_record=check.mx_record,
            spf_record=check.spf_record,
            dkim_record=check.dkim_record,
            dmarc_record=check.dmarc_record,
            score=check.score,
            grade=check.grade,
            issues=check.issues,
            recommendations=check.recommendations,
            security_summary=check.security_summary,
            opt_in_marketing=False,
            created_at=check.created_at,
            updated_at=check.updated_at
        ))
    
    return DomainStatsResponse(
        total_domains=total_domains,
        total_checks=total_checks,
        average_score=float(avg_score_result) if avg_score_result else None,
        domains_by_grade=domains_by_grade,
        recent_checks=recent_check_responses
    )
