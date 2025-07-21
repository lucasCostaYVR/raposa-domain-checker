from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base

class DomainCheck(Base):
    __tablename__ = "domain_checks"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=True, index=True)  # For anonymous users
    domain = Column(String, nullable=False, index=True)
    
    # User relationship (optional for anonymous checks)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    user_domain_id = Column(Integer, ForeignKey("user_domains.id"), nullable=True)

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

    # Relationships
    user = relationship("User", back_populates="domain_checks")
    user_domain = relationship("UserDomain", back_populates="checks")


class DomainUsage(Base):
    __tablename__ = "domain_usage"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, nullable=False, index=True)
    check_count = Column(Integer, default=1)
    last_check = Column(DateTime(timezone=True), server_default=func.now())
    month_year = Column(String, nullable=False, index=True)  # Format: "2025-01"

class User(Base):
    """User model for storing user data from Identity Service"""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True)  # UUID from Identity Service
    email = Column(String, unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email_verified = Column(Boolean, default=False)
    subscription_tier = Column(String, default="free")
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    domains = relationship("UserDomain", back_populates="user", cascade="all, delete-orphan")
    domain_checks = relationship("DomainCheck", back_populates="user", cascade="all, delete-orphan")


class UserDomain(Base):
    """User's managed domains"""
    __tablename__ = "user_domains"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    domain = Column(String, nullable=False, index=True)
    display_name = Column(String, nullable=True)  # User-friendly name
    is_verified = Column(Boolean, default=False)  # Domain ownership verification
    
    # Monitoring settings
    auto_check_enabled = Column(Boolean, default=False)
    check_frequency = Column(String, default="weekly")  # weekly, monthly
    last_auto_check = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="domains")
    checks = relationship("DomainCheck", back_populates="user_domain", cascade="all, delete-orphan")
