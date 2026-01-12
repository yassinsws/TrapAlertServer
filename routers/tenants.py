from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import get_db
from models import User, Tenant, UserRole
from schemas import TenantCreate, TenantResponse, TenantUpdate
from auth import require_role
import secrets

router = APIRouter(prefix="/api/tenants", tags=["Tenants"])

@router.get("", response_model=List[TenantResponse])
async def list_tenants(
    _: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: Session = Depends(get_db)
):
    """List all tenants (Super Admin only)"""
    tenants = db.query(Tenant).all()
    return [TenantResponse.from_orm(t) for t in tenants]

@router.post("", response_model=TenantResponse)
async def create_tenant(
    tenant_data: TenantCreate,
    _: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: Session = Depends(get_db)
):
    """Create a new tenant (Super Admin only)"""
    new_tenant = Tenant(
        name=tenant_data.name,
        company_name=tenant_data.company_name,
        api_key=secrets.token_urlsafe(32)
    )
    
    db.add(new_tenant)
    db.commit()
    db.refresh(new_tenant)
    
    return TenantResponse.from_orm(new_tenant)

@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: int,
    _: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: Session = Depends(get_db)
):
    """Get tenant details (Super Admin only)"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return TenantResponse.from_orm(tenant)

@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: int,
    update: TenantUpdate,
    _: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: Session = Depends(get_db)
):
    """Update tenant (Super Admin only)"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    if update.name is not None:
        tenant.name = update.name
    if update.company_name is not None:
        tenant.company_name = update.company_name
    if update.is_active is not None:
        tenant.is_active = update.is_active
    
    db.commit()
    db.refresh(tenant)
    
    return TenantResponse.from_orm(tenant)

@router.delete("/{tenant_id}")
async def delete_tenant(
    tenant_id: int,
    _: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: Session = Depends(get_db)
):
    """Soft delete tenant (Super Admin only)"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    tenant.is_active = False
    db.commit()
    
    return {"message": "Tenant deactivated successfully"}

@router.post("/{tenant_id}/regenerate-key", response_model=TenantResponse)
async def regenerate_api_key(
    tenant_id: int,
    _: User = Depends(require_role(UserRole.SUPER_ADMIN)),
    db: Session = Depends(get_db)
):
    """Regenerate tenant API key (Super Admin only)"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    tenant.api_key = secrets.token_urlsafe(32)
    db.commit()
    db.refresh(tenant)
    
    return TenantResponse.from_orm(tenant)
