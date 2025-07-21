from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class DomainCheckRequest(BaseModel):
    email: Optional[EmailStr] = None
    domain: str = Field(..., min_length=1, max_length=255)
    opt_in_marketing: bool = False

class DNSRecordResult(BaseModel):
    """Base model for DNS record results"""
    status: str
    issues: List[str] = []
    score: int

class MXRecordResult(DNSRecordResult):
    """MX record analysis result"""
    records: List[Dict[str, Any]] = []

class SPFRecordResult(DNSRecordResult):
    """SPF record analysis result"""
    record: Optional[str] = None
    mechanisms: List[str] = []

class DKIMRecordResult(DNSRecordResult):
    """DKIM record analysis result"""
    selectors: Dict[str, Dict[str, Any]] = {}

class DMARCRecordResult(DNSRecordResult):
    """DMARC record analysis result"""
    record: Optional[str] = None
    policy: Dict[str, str] = {}

class DomainCheckResponse(BaseModel):
    id: int
    email: Optional[str] = None  # Now optional to support anonymous users
    domain: str

    # Enhanced DNS results with user-friendly explanations
    mx_record: Optional[Dict[str, Any]] = None
    spf_record: Optional[Dict[str, Any]] = None
    dkim_record: Optional[Dict[str, Any]] = None
    dmarc_record: Optional[Dict[str, Any]] = None

    # Overall assessment
    score: Optional[int] = None
    grade: Optional[str] = None
    issues: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None

    # New user-friendly summary
    security_summary: Optional[Dict[str, Any]] = None

    # Timestamps
    created_at: datetime
    opt_in_marketing: bool = False

    # Metadata
    opt_in_marketing: bool
    created_at: datetime

    class Config:
        from_attributes = True

class DomainScoreResponse(BaseModel):
    domain: str
    score: int
    mx_score: int
    spf_score: int
    dkim_score: int
    dmarc_score: int
    recommendations: Dict[str, List[str]]

# Authentication Schemas
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    opt_in_marketing: bool = False

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserProfileResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email_verified: bool
    subscription_tier: str
    created_at: datetime
    last_login: Optional[datetime] = None

class UserProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

# Domain Management Schemas
class UserDomainCreateRequest(BaseModel):
    domain: str = Field(..., min_length=1, max_length=255)
    display_name: Optional[str] = Field(None, max_length=100)
    auto_check_enabled: bool = False
    check_frequency: str = Field("weekly", pattern="^(weekly|monthly)$")

class UserDomainUpdateRequest(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    auto_check_enabled: Optional[bool] = None
    check_frequency: Optional[str] = Field(None, pattern="^(weekly|monthly)$")

class UserDomainResponse(BaseModel):
    id: int
    domain: str
    display_name: Optional[str] = None
    is_verified: bool
    auto_check_enabled: bool
    check_frequency: str
    last_auto_check: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Enhanced Domain Check Schemas
class AuthenticatedDomainCheckRequest(BaseModel):
    domain: str = Field(..., min_length=1, max_length=255)
    user_domain_id: Optional[int] = None  # Link to managed domain
    save_to_history: bool = True

class DomainCheckHistoryResponse(BaseModel):
    checks: List[DomainCheckResponse]
    total_count: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

class DomainStatsResponse(BaseModel):
    total_domains: int
    total_checks: int
    average_score: Optional[float] = None
    domains_by_grade: Dict[str, int] = {}
    recent_checks: List[DomainCheckResponse] = []
