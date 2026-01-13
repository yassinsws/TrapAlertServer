from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from db import get_db
from models import User, UserRole
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# HTTP Bearer token scheme
security = HTTPBearer()

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    # Encode password to bytes and hash
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    # Ensure 'sub' is a string for compatibility with python-jose
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"JWT Validation Error: {e}")
        raise credentials_exception

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from the JWT token
    Usage: current_user: User = Depends(get_current_user)
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    user_id_raw = payload.get("sub")
    if user_id_raw is None:
        logger.warning("Token payload missing 'sub' (user ID).")
        raise credentials_exception
    
    try:
        user_id = int(user_id_raw)
    except (ValueError, TypeError):
        logger.warning(f"Invalid user ID format in token: '{user_id_raw}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )
    
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if user is None:
        logger.warning(f"User with ID {user_id} not found or inactive.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user

def require_role(*allowed_roles: UserRole):
    """
    Dependency factory to require specific user roles
    Usage: _: User = Depends(require_role(UserRole.SUPER_ADMIN))
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            logger.warning(f"User {current_user.id} with role {current_user.role} attempted to access resource requiring roles: {[r.value for r in allowed_roles]}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker

def authenticate_user(email: str, password: str, db: Session) -> Optional[User]:
    """Authenticate a user by email and password"""
    email = email.lower().strip()
    logger.info(f"Attempting to authenticate user: '{email}' (len: {len(email)})")
    
    # Try finding user without active filter first for debugging
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        logger.warning(f"User NOT found in DB: '{email}'")
        return None
        
    if not user.is_active:
        logger.warning(f"User found but is INACTIVE: {email}")
        return None
        
    if not verify_password(password, user.password_hash):
        logger.warning(f"Password verification failed for user: {email}")
        return None
        
    logger.info(f"Authentication successful for user: {email}")
    return user
