from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

# Database URL from Railway environment variables
# Use PUBLIC_URL for local development, DATABASE_URL for Railway deployment
DATABASE_URL = os.getenv("DATABASE_PUBLIC_URL") or os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_PUBLIC_URL or DATABASE_URL environment variable is not set.")
    raise ValueError("DATABASE_PUBLIC_URL or DATABASE_URL environment variable is not set")

logger.info("Database URL found, proceeding with PostgreSQL setup.")
# Enhanced connection configuration for better reliability
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "connect_timeout": 10
    },
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
