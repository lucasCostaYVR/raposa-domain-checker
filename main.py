from typing import Union, Optional
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.database import get_db, engine
from src.models import Base, DomainCheck, DomainUsage
from src.schemas import DomainCheckRequest, DomainCheckResponse
from src.dns_utils import check_all_dns_records
from src.email_service import get_email_service
# Force redeploy to clear cached database connection state
import re
import logging
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_db_and_tables():
    import time
    import os
    max_retries = 3
    retry_delay = 2  # Shorter delay for development

    # Check if we're in development mode
    is_development = os.getenv("ENVIRONMENT") == "development"

    for attempt in range(max_retries):
        try:
            if is_development:
                logger.info(f"Development mode: Using create_all for database setup (attempt {attempt + 1}/{max_retries})")
                # In development, just use create_all for simplicity
                Base.metadata.create_all(bind=engine)
                logger.info("Database tables created successfully in development mode.")
                return True
            else:
                logger.info(f"Production mode: Running database migrations... (attempt {attempt + 1}/{max_retries})")

                # Run Alembic migrations for production
                from alembic.config import Config
                from alembic import command

                # Configure Alembic with correct path
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(current_dir)
                alembic_cfg_path = os.path.join(project_root, "alembic.ini")

                # Alternative paths to check for Railway deployment
                alternative_paths = [
                    alembic_cfg_path,  # ../alembic.ini (relative to src/)
                    os.path.join(os.getcwd(), "alembic.ini"),  # ./alembic.ini (current working directory)
                    "alembic.ini",  # Just the filename (current directory)
                ]

                found_config = None
                for path in alternative_paths:
                    if os.path.exists(path):
                        found_config = path
                        logger.info(f"Found Alembic config at: {path}")
                        break

                # Check if alembic.ini exists
                if not found_config:
                    logger.warning(f"Alembic config not found. Tried paths: {alternative_paths}")
                    raise FileNotFoundError("Alembic config not found")

                alembic_cfg = Config(found_config)

                # Run migrations to head
                command.upgrade(alembic_cfg, "head")
                logger.info("Database migrations completed successfully.")
                return True

        except Exception as e:
            logger.error(f"Database setup attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("All database setup attempts failed.")
                # Final fallback to create_all
                try:
                    logger.info("Final fallback: Using create_all...")
                    Base.metadata.create_all(bind=engine)
                    logger.info("Database tables created successfully via fallback.")
                    return True
                except Exception as fallback_e:
                    logger.error(f"Fallback create_all also failed: {fallback_e}")
    return False

# Global flag to track if database is ready
database_ready = False

# Environment-based docs configuration
docs_url = "/docs" if os.getenv("ENVIRONMENT") == "development" else None
redoc_url = "/redoc" if os.getenv("ENVIRONMENT") == "development" else None

app = FastAPI(
    title="Raposa Domain Checker API",
    description="Advanced API for checking domain DNS records including MX, SPF, DKIM, and DMARC with intelligent scoring and email reporting",
    version="2.0.0",
    docs_url=docs_url,
    redoc_url=redoc_url
)

# Configure CORS for frontend development with custom origin checking
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.raposa\.tech|https://raposa\.tech|https://.*\.vercel\.app|https?://localhost:3000|https?://127\.0\.0\.1:3000",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    global database_ready
    logger.info("Starting application...")
    # Try to initialize database, but don't fail if it's not available
    database_ready = create_db_and_tables()
    if not database_ready:
        logger.warning("Database not available at startup. Will retry on first request.")
    logger.info("Application startup completed.")

@app.get("/")
def read_root():
    return {"message": "Raposa Domain Checker API", "version": "1.0.0"}

@app.get("/healthz/")
def health_check_endpoint():
    """Simple health check endpoint for Railway deployment monitoring."""
    # Return ok immediately to allow Railway deployment activation
    # Database initialization happens asynchronously
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

def ensure_database_ready():
    """Ensure database is initialized and ready for use."""
    global database_ready
    if not database_ready:
        logger.info("Database not ready, attempting to initialize...")
        database_ready = create_db_and_tables()
        if not database_ready:
            raise HTTPException(
                status_code=503,
                detail="Database service temporarily unavailable. Please try again later."
            )

async def is_valid_domain(domain: str) -> bool:
    """Validate domain format and safety."""
    # Basic domain validation
    domain_pattern = re.compile(
        r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    )

    if not domain_pattern.match(domain):
        return False

    # Check for private/internal domains
    private_domains = ['localhost', '127.0.0.1', '0.0.0.0', '10.', '192.168.', '172.']
    if any(domain.startswith(private) for private in private_domains):
        return False

    return True

async def send_domain_report_email(email: str, domain: str, analysis_results: dict, is_first_check: bool = False):
    """Background task to send domain report email."""
    try:
        email_service = get_email_service()

        # Send comprehensive domain report
        # Note: Welcome emails are handled by the separate identity service
        success = await email_service.send_domain_report(
            to_email=email,
            domain=domain,
            analysis_results=analysis_results
        )

        if success:
            logger.info(f"Domain report email queued for {email} (domain: {domain})")
        else:
            logger.error(f"Failed to queue domain report email for {email} (domain: {domain})")

    except Exception as e:
        logger.error(f"Error in background email task for {email}, domain {domain}: {e}")

async def check_rate_limits(
    domain: str, 
    email: Optional[str] = None, 
    db: Session = None
) -> tuple[bool, str]:
    """
    Check rate limits for domain checks.
        Returns (is_allowed, limit_message)
    """
    current_month = datetime.now().strftime("%Y-%m")
    
    # Check domain-based limits regardless of email
    domain_usage = db.query(DomainUsage).filter(
        DomainUsage.domain == domain,
        DomainUsage.month_year == current_month
    ).first()

    if email:
        # Registered user - 15 checks per domain per month
        if domain_usage and domain_usage.check_count >= 15:
            return False, "Domain check limit exceeded. Maximum 15 checks per domain per month. Create an account for more checks!"
        return True, ""
    else:
        # Anonymous user - 1 check per domain per month (domain-based, not IP)
        if domain_usage and domain_usage.check_count >= 1:
            return False, "You've already checked this domain this month. Provide an email address for additional checks!"
        return True, ""

@app.post("/check-domain", response_model=DomainCheckResponse)
async def check_domain(
    request: DomainCheckRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Perform comprehensive domain security analysis including MX, SPF, DKIM, and DMARC records.

    - **domain**: Domain name to analyze (e.g., example.com)
    - **email**: Email address for results delivery (optional for first check)
    - **opt_in_marketing**: Whether to receive marketing emails

    Returns detailed security analysis with scoring and recommendations.
    """

    try:
        # Ensure database is ready
        ensure_database_ready()

        # Validate domain format and safety
        if not await is_valid_domain(request.domain):
            raise HTTPException(status_code=422, detail="Invalid or unsafe domain format")

        # Use default email for anonymous users to prevent email service issues
        effective_email = request.email or "anonymous@raposa.tech"
        
        logger.info(f"Domain check requested for {request.domain} by {request.email or 'anonymous user'}")

        # Check rate limits using our progressive system
        is_allowed, limit_message = await check_rate_limits(
            domain=request.domain,
            email=request.email,
            db=db
        )

        if not is_allowed:
            raise HTTPException(status_code=429, detail=limit_message)

        # Perform comprehensive DNS analysis
        dns_analysis = await check_all_dns_records(request.domain)

        # Create domain check record with enhanced data
        domain_check = DomainCheck(
            email=effective_email,
            domain=request.domain,
            mx_record=dns_analysis["mx"],
            spf_record=dns_analysis["spf"],
            dkim_record=dns_analysis["dkim"],
            dmarc_record=dns_analysis["dmarc"],
            score=dns_analysis["total_score"],
            grade=dns_analysis["grade"],
            issues=dns_analysis["issues"],
            recommendations=dns_analysis["recommendations"],
            security_summary=dns_analysis["security_summary"],
            opt_in_marketing=request.opt_in_marketing
        )

        db.add(domain_check)

        # Update usage tracking - simple domain-based tracking for all users
        current_month = datetime.now().strftime("%Y-%m")
        
        domain_usage = db.query(DomainUsage).filter(
            DomainUsage.domain == request.domain,
            DomainUsage.month_year == current_month
        ).first()
        
        if domain_usage:
            domain_usage.check_count += 1
            domain_usage.last_check = datetime.now()
        else:
            domain_usage = DomainUsage(
                domain=request.domain,
                check_count=1,
                month_year=current_month
            )
            db.add(domain_usage)
        
        db.commit()
        db.refresh(domain_check)

        # Schedule background email sending only if email provided
        if request.email:
            # Check if this is the user's first domain check (for welcome email)
            user_check_count = db.query(DomainCheck).filter(
                DomainCheck.email == request.email
            ).count()
            is_first_check = user_check_count == 1

            background_tasks.add_task(
                send_domain_report_email,
                email=request.email,
                domain=request.domain,
                analysis_results={
                    "domain": request.domain,
                    "score": dns_analysis["total_score"],
                    "grade": dns_analysis["grade"],
                    "mx_record": dns_analysis["mx"],
                    "spf_record": dns_analysis["spf"],
                    "dkim_record": dns_analysis["dkim"],
                    "dmarc_record": dns_analysis["dmarc"],
                    "issues": dns_analysis["issues"],
                    "recommendations": dns_analysis["recommendations"],
                    "security_summary": dns_analysis["security_summary"],
                    "created_at": domain_check.created_at.isoformat()
                },
                is_first_check=is_first_check
            )

        logger.info(f"Domain check completed for {request.domain} - Score: {dns_analysis['total_score']}, Grade: {dns_analysis['grade']} - Email report scheduled")

        # Return the domain check but with original email (null for anonymous users)
        response_data = {
            "id": domain_check.id,
            "email": request.email,  # Return original email, not effective_email
            "domain": domain_check.domain,
            "mx_record": domain_check.mx_record,
            "spf_record": domain_check.spf_record,
            "dkim_record": domain_check.dkim_record,
            "dmarc_record": domain_check.dmarc_record,
            "score": domain_check.score,
            "grade": domain_check.grade,
            "issues": domain_check.issues,
            "recommendations": domain_check.recommendations,
            "security_summary": domain_check.security_summary,
            "created_at": domain_check.created_at,
            "opt_in_marketing": domain_check.opt_in_marketing
        }
        
        return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in check_domain for {request.domain}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error during domain analysis")

@app.get("/domain-usage/{domain}")
async def get_domain_usage(domain: str, db: Session = Depends(get_db)):
    """Get current month usage for a domain"""
    # Ensure database is ready
    ensure_database_ready()

    current_month = datetime.now().strftime("%Y-%m")
    usage = db.query(DomainUsage).filter(
        DomainUsage.domain == domain,
        DomainUsage.month_year == current_month
    ).first()

    if not usage:
        return {"domain": domain, "checks_used": 0, "checks_remaining": 5}

    return {
        "domain": domain,
        "checks_used": usage.check_count,
        "checks_remaining": max(0, 5 - usage.check_count)
    }

@app.get("/debug/email-service")
async def get_email_service_info():
    """
    Debug endpoint to check email service status.
    Shows if SendGrid is configured and service information.
    """
    try:
        email_service = get_email_service()
        service_info = email_service.get_service_info()
        return {
            "status": "success",
            "service_info": service_info
        }
    except Exception as e:
        logger.error(f"Error checking email service: {e}")
        raise HTTPException(status_code=500, detail=f"Email service error: {str(e)}")
