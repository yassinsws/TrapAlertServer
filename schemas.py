from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from models import UserRole, ReportStatus, IntegrationType

# ============ User Schemas ============
class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.CLIENT_USER
    tenant_id: Optional[int] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    tenant_id: Optional[int] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ============ Tenant Schemas ============
class TenantBase(BaseModel):
    name: str
    company_name: Optional[str] = None

class TenantCreate(TenantBase):
    pass

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    is_active: Optional[bool] = None

class TenantResponse(TenantBase):
    id: int
    api_key: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ============ Integration Schemas ============
class IntegrationBase(BaseModel):
    integration_type: IntegrationType
    config_json: dict = {}
    enabled: bool = True

class IntegrationCreate(IntegrationBase):
    tenant_id: int

class IntegrationUpdate(BaseModel):
    config_json: Optional[dict] = None
    enabled: Optional[bool] = None

class IntegrationResponse(IntegrationBase):
    id: int
    tenant_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ============ BugReport Schemas ============
class BugReportBase(BaseModel):
    description: Optional[str] = None
    label: List[str] = []
    struggle_score: Optional[float] = None
    metadata_json: str
    dom_snapshot: str

class BugReportCreate(BugReportBase):
    tenant_id: int

class BugReportUpdate(BaseModel):
    status: Optional[ReportStatus] = None
    synced_to_integration: Optional[bool] = None
    external_ticket_id: Optional[str] = None

class BugReportResponse(BugReportBase):
    id: int
    tenant_id: int
    status: ReportStatus
    synced_to_integration: bool
    external_ticket_id: Optional[str]
    video_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class BugReportListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    reports: List[BugReportResponse]

# ============ Analytics Schemas ============
class DashboardStats(BaseModel):
    total_reports: int
    active_tenants: int
    resolved_this_week: int
    avg_struggle_score: float
