from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from db import get_db
from models import User, UserRole
from schemas import UserCreate, UserResponse, UserUpdate
from auth import hash_password, get_current_user, require_role

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List users
    - Super admins can see all users
    - Client admins can see users in their tenant
    - Regular users cannot access this endpoint
    """
    if current_user.role == UserRole.CLIENT_USER:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    if current_user.role == UserRole.SUPER_ADMIN:
        users = db.query(User).all()
    else:
        users = db.query(User).filter(User.tenant_id == current_user.tenant_id).all()
    
    return [UserResponse.from_orm(u) for u in users]

@router.post("", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new user
    - Super admins can create users for any tenant
    - Client admins can create users for their own tenant
    """
    if current_user.role == UserRole.CLIENT_USER:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Client admins can only create users for their own tenant
    if current_user.role == UserRole.CLIENT_ADMIN:
        if user_data.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Can only create users for your own tenant")
        if user_data.role == UserRole.SUPER_ADMIN:
            raise HTTPException(status_code=403, detail="Cannot create super admin users")
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        tenant_id=user_data.tenant_id
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse.from_orm(new_user)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user details"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check permissions
    if current_user.role == UserRole.CLIENT_USER:
        if user.id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
    elif current_user.role == UserRole.CLIENT_ADMIN:
        if user.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return UserResponse.from_orm(user)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user"""
    if current_user.role == UserRole.CLIENT_USER:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Client admins can only update users in their tenant
    if current_user.role == UserRole.CLIENT_ADMIN:
        if user.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
        if update.role == UserRole.SUPER_ADMIN:
            raise HTTPException(status_code=403, detail="Cannot assign super admin role")
    
    # Update fields
    if update.email is not None:
        user.email = update.email
    if update.role is not None:
        user.role = update.role
    if update.tenant_id is not None:
        user.tenant_id = update.tenant_id
    if update.is_active is not None:
        user.is_active = update.is_active
    
    db.commit()
    db.refresh(user)
    
    return UserResponse.from_orm(user)

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete user"""
    if current_user.role == UserRole.CLIENT_USER:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Client admins can only delete users in their tenant
    if current_user.role == UserRole.CLIENT_ADMIN:
        if user.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    user.is_active = False
    db.commit()
    
    return {"message": "User deactivated successfully"}
