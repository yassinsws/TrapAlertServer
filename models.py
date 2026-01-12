from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Boolean, Enum as SQLEnum, LargeBinary
from sqlalchemy.orm import relationship
from db import Base
from datetime import datetime
import enum
import secrets

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    CLIENT_ADMIN = "CLIENT_ADMIN"
    CLIENT_USER = "CLIENT_USER"

class ReportStatus(str, enum.Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class IntegrationType(str, enum.Enum):
    JIRA = "JIRA"
    CLICKUP = "CLICKUP"
    LINEAR = "LINEAR"

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    company_name = Column(String, nullable=True)
    api_key = Column(String, unique=True, nullable=False, default=lambda: secrets.token_urlsafe(32))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="tenant")
    bug_reports = relationship("BugReport", back_populates="tenant")
    integrations = relationship("Integration", back_populates="tenant")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.CLIENT_USER)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)  # Nullable for super admins
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")

class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    integration_type = Column(SQLEnum(IntegrationType), nullable=False)
    config_json = Column(JSON, default={})  # Store OAuth tokens, project IDs, etc.
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="integrations")

class BugReport(Base):
    __tablename__ = "bug_reports"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    description = Column(String, nullable=True)
    label = Column(JSON, default=[])
    struggle_score = Column(Float, nullable=True)
    metadata_json = Column(String)
    dom_snapshot = Column(String)
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.NEW)
    synced_to_integration = Column(Boolean, default=False)
    external_ticket_id = Column(String, nullable=True)
    video_blob = Column(LargeBinary, nullable=True)
    video_mime_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="bug_reports")
