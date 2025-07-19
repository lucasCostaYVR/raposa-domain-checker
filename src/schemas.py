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
