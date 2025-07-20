from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text
from sqlalchemy.sql import func
from src.database import Base

"""
SQLAlchemy Models
Define your database models here.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Add your models here
# Example:
# class User(Base):
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String(255), unique=True, nullable=False, index=True)
#     username = Column(String(100), unique=True, nullable=False, index=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     is_active = Column(Boolean, default=True)

class DomainUsage(Base):
    __tablename__ = "domain_usage"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, nullable=False, index=True)
    check_count = Column(Integer, default=1)
    last_check = Column(DateTime(timezone=True), server_default=func.now())
    month_year = Column(String, nullable=False, index=True)  # Format: "2025-01"
