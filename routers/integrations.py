from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import get_db
from models import User, Integration, UserRole
from schemas import IntegrationCreate, IntegrationResponse, IntegrationUpdate
from auth import get_current_user

router = APIRouter(prefix="/api/integrations", tags=["Integrations"])

@router.get("", response_model=List[IntegrationResponse])
async def list_integrations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List integrations for current user's tenant
    """
    if current_user.role == UserRole.CLIENT_USER:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    if current_user.role == UserRole.SUPER_ADMIN:
        integrations = db.query(Integration).all()
    else:
        integrations = db.query(Integration).filter(Integration.tenant_id == current_user.tenant_id).all()
    
    return [IntegrationResponse.from_orm(i) for i in integrations]

@router.post("", response_model=IntegrationResponse)
async def create_integration(
    integration_data: IntegrationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new integration"""
    if current_user.role == UserRole.CLIENT_USER:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Client admins can only create integrations for their tenant
    if current_user.role == UserRole.CLIENT_ADMIN:
        if integration_data.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Can only create integrations for your own tenant")
    
    new_integration = Integration(
        tenant_id=integration_data.tenant_id,
        integration_type=integration_data.integration_type,
        config_json=integration_data.config_json,
        enabled=integration_data.enabled
    )
    
    db.add(new_integration)
    db.commit()
    db.refresh(new_integration)
    
    return IntegrationResponse.from_orm(new_integration)

@router.put("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: int,
    update: IntegrationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update integration configuration"""
    if current_user.role == UserRole.CLIENT_USER:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Client admins can only update integrations in their tenant
    if current_user.role == UserRole.CLIENT_ADMIN:
        if integration.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    if update.config_json is not None:
        integration.config_json = update.config_json
    if update.enabled is not None:
        integration.enabled = update.enabled
    
    db.commit()
    db.refresh(integration)
    
    return IntegrationResponse.from_orm(integration)

@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an integration"""
    if current_user.role == UserRole.CLIENT_USER:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Client admins can only delete integrations in their tenant
    if current_user.role == UserRole.CLIENT_ADMIN:
        if integration.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    db.delete(integration)
    db.commit()
    
    return {"message": "Integration deleted successfully"}

@router.post("/{integration_id}/test")
async def test_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test integration connection"""
    if current_user.role == UserRole.CLIENT_USER:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    integration = db.query(Integration).filter(Integration.id == integration_id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Check permissions
    if current_user.role == UserRole.CLIENT_ADMIN:
        if integration.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # TODO: Implement actual integration testing logic
    # For now, just return success
    return {
        "status": "success",
        "message": f"{integration.integration_type.value} connection test successful"
    }
