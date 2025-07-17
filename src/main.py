from typing import Union
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine
from models import Base, DomainCheck, DomainUsage
from schemas import DomainCheckRequest, DomainCheckResponse
from dns_utils import check_all_dns_records
from email_service import get_email_service
import re
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_db_and_tables():
    import time
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            logger.info(f"Creating database tables... (attempt {attempt + 1}/{max_retries})")
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully.")
            return True
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("All database connection attempts failed.")
    return False

# Global flag to track if database is ready
database_ready = False

app = FastAPI(
    title="Raposa Domain Checker API",
    description="Advanced API for checking domain DNS records including MX, SPF, DKIM, and DMARC with intelligent scoring and email reporting",
    version="2.0.0"
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
    return {"status": "ok"}

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

        # Send welcome email for first-time users (optional)
        if is_first_check:
            await email_service.send_welcome_email(email, domain)

        # Send comprehensive domain report
        success = await email_service.send_domain_report(
            to_email=email,
            domain=domain,
            analysis_results=analysis_results,
            include_pdf=True
        )

        if success:
            logger.info(f"Domain report email sent successfully to {email} for {domain}")
        else:
            logger.error(f"Failed to send domain report email to {email} for {domain}")

    except Exception as e:
        logger.error(f"Error in background email task for {email}, domain {domain}: {e}")

@app.post("/check-domain", response_model=DomainCheckResponse)
async def check_domain(request: DomainCheckRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Perform comprehensive domain security analysis including MX, SPF, DKIM, and DMARC records.

    - **domain**: Domain name to analyze (e.g., example.com)
    - **email**: Email address for results delivery
    - **opt_in_marketing**: Whether to receive marketing emails

    Returns detailed security analysis with scoring and recommendations.
    """

    try:
        # Ensure database is ready
        ensure_database_ready()

        # Validate domain format and safety
        if not await is_valid_domain(request.domain):
            raise HTTPException(status_code=422, detail="Invalid or unsafe domain format")

        logger.info(f"Domain check requested for {request.domain} by {request.email}")

        # Check monthly usage limit (5 checks per domain per month)
        current_month = datetime.now().strftime("%Y-%m")
        domain_usage = db.query(DomainUsage).filter(
            DomainUsage.domain == request.domain,
            DomainUsage.month_year == current_month
        ).first()

        if domain_usage and domain_usage.check_count >= 5:
            raise HTTPException(
                status_code=429,
                detail="Domain check limit exceeded. Maximum 5 checks per domain per month."
            )

        # Perform comprehensive DNS analysis
        dns_analysis = await check_all_dns_records(request.domain)

        # Create domain check record with enhanced data
        domain_check = DomainCheck(
            email=request.email,
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

        # Update domain usage
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

        # Check if this is the user's first domain check (for welcome email)
        user_check_count = db.query(DomainCheck).filter(
            DomainCheck.email == request.email
        ).count()
        is_first_check = user_check_count == 1

        # Schedule background email sending
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

        return domain_check

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
