from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List
from datetime import datetime, timedelta
from db import get_db
from models import User, BugReport, Tenant, UserRole, ReportStatus
from schemas import BugReportResponse, BugReportListResponse, BugReportUpdate, DashboardStats
from auth import get_current_user, require_role

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    # Build query based on user role
    if current_user.role == UserRole.SUPER_ADMIN:
        reports_query = db.query(BugReport)
        tenants_query = db.query(Tenant)
    else:
        reports_query = db.query(BugReport).filter(BugReport.tenant_id == current_user.tenant_id)
        tenants_query = db.query(Tenant).filter(Tenant.id == current_user.tenant_id)
    
    # Calculate stats
    total_reports = reports_query.count()
    active_tenants = tenants_query.filter(Tenant.is_active == True).count()
    
    # Reports resolved this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    resolved_this_week = reports_query.filter(
        and_(
            BugReport.status == ReportStatus.RESOLVED,
            BugReport.created_at >= week_ago
        )
    ).count()
    
    # Average struggle score
    avg_score_result = reports_query.filter(BugReport.struggle_score.isnot(None)).with_entities(
        func.avg(BugReport.struggle_score)
    ).scalar()
    avg_struggle_score = float(avg_score_result) if avg_score_result else 0.0
    
    return DashboardStats(
        total_reports=total_reports,
        active_tenants=active_tenants,
        resolved_this_week=resolved_this_week,
        avg_struggle_score=round(avg_struggle_score, 2)
    )

@router.get("", response_model=BugReportListResponse)
async def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[ReportStatus] = None,
    tenant_id: Optional[int] = None,
    search: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List bug reports with filtering and pagination
    - Super admins can see all reports and filter by tenant
    - Client users can only see their own tenant's reports
    """
    # Base query
    query = db.query(BugReport)
    
    # Apply tenant filtering based on user role
    if current_user.role != UserRole.SUPER_ADMIN:
        # Client users can only see their tenant's reports
        query = query.filter(BugReport.tenant_id == current_user.tenant_id)
    elif tenant_id is not None:
        # Super admin filtering by specific tenant
        query = query.filter(BugReport.tenant_id == tenant_id)
    
    # Apply filters
    if status:
        query = query.filter(BugReport.status == status)
    
    if search:
        query = query.filter(
            or_(
                BugReport.description.ilike(f"%{search}%"),
                BugReport.metadata_json.ilike(f"%{search}%")
            )
        )
    
    if date_from:
        query = query.filter(BugReport.created_at >= date_from)
    
    if date_to:
        query = query.filter(BugReport.created_at <= date_to)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    reports = query.order_by(BugReport.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return BugReportListResponse(
        total=total,
        page=page,
        page_size=page_size,
        reports=[BugReportResponse.from_orm(r) for r in reports]
    )

@router.get("/{report_id}", response_model=BugReportResponse)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single bug report by ID"""
    report = db.query(BugReport).filter(BugReport.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check permissions: client users can only see their tenant's reports
    if current_user.role != UserRole.SUPER_ADMIN and report.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return BugReportResponse.from_orm(report)

@router.put("/{report_id}/status", response_model=BugReportResponse)
async def update_report_status(
    report_id: int,
    update: BugReportUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a bug report's status"""
    report = db.query(BugReport).filter(BugReport.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check permissions
    if current_user.role != UserRole.SUPER_ADMIN and report.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    if update.status is not None:
        report.status = update.status
    if update.synced_to_integration is not None:
        report.synced_to_integration = update.synced_to_integration
    if update.external_ticket_id is not None:
        report.external_ticket_id = update.external_ticket_id
    
    db.commit()
    db.refresh(report)
    
    return BugReportResponse.from_orm(report)


@router.get("/{report_id}/video")
async def get_report_video(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download the compressed video for a bug report.
    Enforces role-based access control and tenant isolation.
    """
    report = db.query(BugReport).filter(BugReport.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    # Check permissions
    if current_user.role != UserRole.SUPER_ADMIN:
        if report.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
    # Video is now accessed via video_url in the report object
    return None

@router.delete("/{report_id}", status_code=204)
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a bug report permanently"""
    report = db.query(BugReport).filter(BugReport.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    # Permission check
    if current_user.role != UserRole.SUPER_ADMIN:
        if report.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
    db.delete(report)
    db.commit()
    return None

class ReportUpdate(BaseModel):
    description: str | None = None
    label: List[str] | None = None

@router.put("/{report_id}", response_model=BugReportResponse)
async def update_report_details(
    report_id: int,
    update_data: ReportUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update report description and labels"""
    report = db.query(BugReport).filter(BugReport.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    # Permission check
    if current_user.role != UserRole.SUPER_ADMIN:
        if report.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
            
    if update_data.description is not None:
        report.description = update_data.description
        
    if update_data.label is not None:
        report.label = update_data.label
        
    db.commit()
    db.refresh(report)
    return BugReportResponse.from_orm(report)
