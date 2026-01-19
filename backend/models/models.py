"""
OhmVision - Database Models
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import enum
from datetime import datetime

# Enums
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    SUPPORT = "support"
    CLIENT_ADMIN = "client_admin"
    CLIENT_USER = "client_user"

class PackageType(str, enum.Enum):
    STARTER = "starter"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"
    PLATINUM = "platinum"

class ContractStatus(str, enum.Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class AlertSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(str, enum.Enum):
    PERSON_DETECTED = "person_detected"
    INTRUSION = "intrusion"
    FALL_DETECTED = "fall_detected"
    MAN_DOWN = "man_down"
    PPE_MISSING = "ppe_missing"
    FIRE_DETECTED = "fire_detected"
    SMOKE_DETECTED = "smoke_detected"
    VEHICLE_DETECTED = "vehicle_detected"
    LICENSE_PLATE = "license_plate"
    CROWD_DETECTED = "crowd_detected"
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"
    SYSTEM_ERROR = "system_error"

class DeploymentType(str, enum.Enum):
    CLOUD = "cloud"
    ON_PREMISE = "on_premise"
    HYBRID = "hybrid"

# =============================================================================
# USERS & AUTH
# =============================================================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.CLIENT_USER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Relations
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    client = relationship("Client", back_populates="users")
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)

# =============================================================================
# CLIENTS & CONTRACTS
# =============================================================================

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    company_name = Column(String(255))
    email = Column(String(255), nullable=False)
    phone = Column(String(50))
    address = Column(Text)
    city = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100), default="France")
    
    # Billing
    siret = Column(String(20))
    vat_number = Column(String(50))
    stripe_customer_id = Column(String(255))
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relations
    users = relationship("User", back_populates="client")
    contracts = relationship("Contract", back_populates="client")
    cameras = relationship("Camera", back_populates="client")
    sites = relationship("Site", back_populates="client")
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    # Package
    package = Column(Enum(PackageType), nullable=False)
    deployment_type = Column(Enum(DeploymentType), default=DeploymentType.CLOUD)
    
    # Pricing
    price_monthly = Column(Float, nullable=False)
    price_yearly = Column(Float)
    is_yearly = Column(Boolean, default=False)
    discount_percent = Column(Float, default=0)
    
    # Limits
    max_cameras = Column(Integer, default=4)
    max_users = Column(Integer, default=5)
    
    # Features (JSON array)
    features = Column(JSON, default=[])
    
    # Status
    status = Column(Enum(ContractStatus), default=ContractStatus.TRIAL)
    trial_ends_at = Column(DateTime, nullable=True)
    
    # Dates
    start_date = Column(DateTime, server_default=func.now())
    end_date = Column(DateTime, nullable=True)
    next_billing_date = Column(DateTime, nullable=True)
    
    # Stripe
    stripe_subscription_id = Column(String(255))
    
    # Relations
    client = relationship("Client", back_populates="contracts")
    invoices = relationship("Invoice", back_populates="contract")
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# =============================================================================
# SITES & CAMERAS
# =============================================================================

class Site(Base):
    __tablename__ = "sites"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    address = Column(Text)
    city = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100), default="France")
    
    # Deployment
    deployment_type = Column(Enum(DeploymentType), default=DeploymentType.CLOUD)
    server_ip = Column(String(50))  # Pour on-premise
    
    is_active = Column(Boolean, default=True)
    
    # Relations
    client = relationship("Client", back_populates="sites")
    cameras = relationship("Camera", back_populates="site")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Camera(Base):
    __tablename__ = "cameras"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True)
    
    # Info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    location = Column(String(255))
    
    # Connection
    rtsp_url = Column(String(500))
    ip_address = Column(String(50))
    port = Column(Integer, default=554)
    username = Column(String(100))
    password = Column(String(255))  # Encrypted
    
    # Status
    is_active = Column(Boolean, default=True)
    is_online = Column(Boolean, default=False)
    last_seen = Column(DateTime, nullable=True)
    
    # Capabilities
    resolution_width = Column(Integer)
    resolution_height = Column(Integer)
    fps = Column(Integer, default=15)
    
    # AI Config (JSON)
    detection_config = Column(JSON, default={
        "person_detection": True,
        "counting": False,
        "fall_detection": False,
        "ppe_detection": False,
        "fire_detection": False,
        "vehicle_detection": False,
        "zones": []
    })
    
    # Detection zones (JSON array of polygons)
    zones = Column(JSON, default=[])
    
    # Relations
    client = relationship("Client", back_populates="cameras")
    site = relationship("Site", back_populates="cameras")
    alerts = relationship("Alert", back_populates="camera")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# =============================================================================
# ALERTS & EVENTS
# =============================================================================

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    
    # Alert info
    type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.MEDIUM)
    message = Column(Text, nullable=False)
    
    # Detection data (JSON)
    data = Column(JSON, default={})
    
    # Media
    snapshot_url = Column(String(500))
    video_clip_url = Column(String(500))
    
    # Status
    is_read = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # AI Agent
    ai_analyzed = Column(Boolean, default=False)
    ai_response = Column(Text, nullable=True)
    
    # Relations
    camera = relationship("Camera", back_populates="alerts")
    
    created_at = Column(DateTime, server_default=func.now())

# =============================================================================
# ANALYTICS & STATS
# =============================================================================

class DailyStat(Base):
    __tablename__ = "daily_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    
    # Counting
    total_entries = Column(Integer, default=0)
    total_exits = Column(Integer, default=0)
    peak_count = Column(Integer, default=0)
    peak_time = Column(DateTime, nullable=True)
    
    # Alerts
    total_alerts = Column(Integer, default=0)
    critical_alerts = Column(Integer, default=0)
    
    # PPE
    ppe_compliance_rate = Column(Float, default=100.0)
    
    # Hourly breakdown (JSON)
    hourly_data = Column(JSON, default={})
    
    created_at = Column(DateTime, server_default=func.now())

# =============================================================================
# BILLING
# =============================================================================

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    
    # Invoice info
    invoice_number = Column(String(50), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="EUR")
    
    # Status
    status = Column(String(20), default="pending")  # pending, paid, failed, refunded
    
    # Dates
    invoice_date = Column(DateTime, server_default=func.now())
    due_date = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    
    # Stripe
    stripe_invoice_id = Column(String(255))
    stripe_payment_intent_id = Column(String(255))
    
    # PDF
    pdf_url = Column(String(500))
    
    # Relations
    contract = relationship("Contract", back_populates="invoices")
    
    created_at = Column(DateTime, server_default=func.now())

# =============================================================================
# SUPPORT & TICKETS
# =============================================================================

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Ticket info
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    category = Column(String(50))  # technical, billing, feature, other
    
    # Status
    status = Column(String(20), default="open")  # open, in_progress, waiting, resolved, closed
    
    # AI Agent
    ai_handled = Column(Boolean, default=False)
    ai_response = Column(Text, nullable=True)
    ai_resolved = Column(Boolean, default=False)
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Resolution
    resolution = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class TicketMessage(Base):
    __tablename__ = "ticket_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    message = Column(Text, nullable=False)
    is_from_ai = Column(Boolean, default=False)
    is_internal = Column(Boolean, default=False)
    
    attachments = Column(JSON, default=[])
    
    created_at = Column(DateTime, server_default=func.now())

# =============================================================================
# SYSTEM SETTINGS
# =============================================================================

class SystemSettings(Base):
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=False)
    category = Column(String(50), default="general")  # general, ai, storage, notifications, etc.
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
