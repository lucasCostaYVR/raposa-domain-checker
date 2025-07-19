from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text
from sqlalchemy.sql import func
from src.database import Base

class DomainCheck(Base):
    __tablename__ = "domain_checks"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=True, index=True)  # Now optional
    domain = Column(String, nullable=False, index=True)

    # Enhanced DNS record storage
    mx_record = Column(JSON, nullable=True)         # Full MX analysis
    spf_record = Column(JSON, nullable=True)        # Full SPF analysis
    dkim_record = Column(JSON, nullable=True)       # DKIM selectors and analysis
    dmarc_record = Column(JSON, nullable=True)      # Full DMARC analysis

    # Overall assessment
    score = Column(Integer, nullable=True)
    grade = Column(String(5), nullable=True)        # Letter grade (A+, A, B+, etc.)
    issues = Column(JSON, nullable=True)            # List of security issues found
    recommendations = Column(JSON, nullable=True)   # Actionable recommendations
    security_summary = Column(JSON, nullable=True)  # User-friendly security summary

    # Metadata
    opt_in_marketing = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DomainUsage(Base):
    __tablename__ = "domain_usage"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, nullable=False, index=True)
    check_count = Column(Integer, default=1)
    last_check = Column(DateTime(timezone=True), server_default=func.now())
    month_year = Column(String, nullable=False, index=True)  # Format: "2025-01"
