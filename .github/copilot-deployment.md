# Deployment and Infrastructure Instructions

## AI Assistant Guidelines
- **Be brief and direct**: Provide concise, actionable responses without unnecessary explanation
- **Prioritize scripts**: Always recommend project scripts over manual commands
- **Update documentation**: When making changes, update these instruction files to keep them current
- **Stay focused**: Address the specific request without verbose context

## Automated Deployment with Helper Scripts

### Recommended Deployment Workflow
**Always use the provided scripts instead of manual commands:**

```bash
# Development deployment
./scripts/railway.sh deploy-dev     # Deploys current branch to staging

# Production deployment
./scripts/railway.sh deploy-prod    # Merges develop→main, deploys to production

# Environment management
./scripts/railway.sh switch dev     # Switch to development environment
./scripts/railway.sh switch prod    # Switch to production environment
./scripts/railway.sh health         # Check both environments
./scripts/railway.sh status         # Current Railway status
```

### Emergency Operations
```bash
# Quick rollback
./scripts/railway.sh rollback

# View logs
./scripts/railway.sh logs

# Check deployments
./scripts/railway.sh deployments
```

### Git-Integrated Deployment
```bash
# Feature development (auto-deploys to staging)
./scripts/git.sh feature new-feature
./scripts/git.sh commit "Add feature"
./scripts/git.sh finish-feature     # Triggers staging deployment

# Production release
./scripts/git.sh release            # Triggers production deployment
```

## Railway Deployment Patterns

### Nixpacks Configuration (CURRENT - WORKING)

#### Railway Configuration
```json
{
    "build": {
        "builder": "nixpacks"
    },
    "deploy": {
        "healthcheckPath": "/healthz/",
        "healthcheckTimeout": 120,
        "restartPolicyType": "ON_FAILURE",
        "startCommand": "gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 --keep-alive 5"
    }
}
```

#### Project Structure Requirements
```
main.py                  # FastAPI app in PROJECT ROOT (not src/)
src/
├── database.py          # Import: from src.database import get_db
├── models.py            # Import: from src.models import Base
├── schemas.py           # Import: from src.schemas import DomainCheckRequest
├── dns_utils.py         # Import: from src.dns_utils import check_all_dns_records
└── email_service.py     # Import: from src.email_service import get_email_service
railway.json             # Deployment configuration
requirements.txt         # Python dependencies
```

#### Critical Success Factors
- **Disable Dockerfile**: Rename to `Dockerfile.disabled` to force nixpacks
- **No custom nixpacks.toml**: Let auto-detection work (most reliable)
- **main.py in root**: Required for `gunicorn main:app` to work
- **Import pattern**: Use `from src.module` imports in main.py
- **SQLAlchemy**: Use `from sqlalchemy import text` for raw queries
- **Health checks**: Must return 200 status quickly for deployment activation

# Copy requirements first for better caching
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Copy application code
COPY ./src /code

# Create startup script
RUN printf "#!/bin/bash\n" > ./paracord_runner.sh && \
    printf "RUN_PORT=\"\${PORT:-8000}\"\n\n" >> ./paracord_runner.sh && \
    printf "gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind \"[::]:\$RUN_PORT\"\n" >> ./paracord_runner.sh

RUN chmod +x paracord_runner.sh

# Clean up
RUN apt-get remove --purge -y gcc && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Expose port
EXPOSE 8000

# Run application
CMD ["./paracord_runner.sh"]
```

### Environment Configuration

#### Environment Variables Structure
```bash
# Production Environment (.env.production)
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@host:port/db
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=noreply@raposa.tech

# Development Environment (.env.development)
ENVIRONMENT=development
DATABASE_URL=postgresql://user:pass@localhost:5432/raposa_dev
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=dev@raposa.tech
```

#### Railway GitHub Integration Configuration
Since you're using GitHub source instead of Dockerfile:

```bash
# Railway will auto-detect Python application and use:
# - requirements.txt for dependencies
# - Gunicorn for WSGI server
# - PORT environment variable for binding

# Railway auto-generated build process:
# 1. pip install -r requirements.txt
# 2. gunicorn main:app --bind 0.0.0.0:$PORT
```

#### Manual Environment Configuration (if needed)
```bash
# Set environment variables in Railway dashboard or CLI
railway variables set ENVIRONMENT=production
railway variables set DATABASE_URL=${{ Postgres.DATABASE_URL }}
railway variables set SENDGRID_API_KEY=your_api_key
railway variables set SENDGRID_FROM_EMAIL=noreply@raposa.tech
```

### Branch-Based Deployment Strategy

#### Automatic GitHub Deployment Setup
Since Railway is connected to GitHub source (not Dockerfile), deployments are now automatic:

**Production Environment:**
- **Service**: `raposa-app-api`
- **Source**: GitHub repository `lucasCostaYVR/raposa-domain-checker`
- **Branch**: `main`
- **Root Directory**: `/`
- **Build Command**: Auto-detected from `requirements.txt`
- **Start Command**: Auto-detected from Python app

**Development Environment:**
- **Service**: `raposa-stage`
- **Source**: GitHub repository `lucasCostaYVR/raposa-domain-checker`
- **Branch**: `develop`
- **Root Directory**: `/`
- **Build Command**: Auto-detected from `requirements.txt`
- **Start Command**: Auto-detected from Python app

#### Deployment Workflow (Automatic)
```bash
# Deploy to development
git checkout develop
git add .
git commit -m "Feature changes"
git push origin develop
# ↑ Automatically deploys to stage.domainchecker.raposa.tech

# Deploy to production
git checkout main
git merge develop
git push origin main
# ↑ Automatically deploys to api.domainchecker.raposa.tech
```

### Manual Deployment (If Needed)
**⚠️ Only use manual deployment if automated scripts fail:**

```bash
# Manual deployment to current linked environment
railway up

# Or redeploy latest commit
railway redeploy
```

**Prefer using scripts:**
```bash
./scripts/railway.sh deploy-dev    # For development
./scripts/railway.sh deploy-prod   # For production
```

### Database Migration Management

#### Production Migration Strategy
```python
def create_db_and_tables():
    """Environment-aware database setup."""
    import os
    from alembic.config import Config
    from alembic import command

    is_development = os.getenv("ENVIRONMENT") == "development"

    if is_development:
        # Development: Use create_all for simplicity
        Base.metadata.create_all(bind=engine)
        logger.info("Development database tables created")
    else:
        # Production: Use Alembic migrations
        try:
            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")
            logger.info("Production database migrations completed")
        except Exception as e:
            logger.warning(f"Migration failed, falling back to create_all: {e}")
            Base.metadata.create_all(bind=engine)
```

#### Migration Deployment Process
**Use the automated scripts for migrations:**

```bash
# Create migration (automatically formats properly)
./scripts/railway.sh migrate "Description of changes"

# Test on development (automatic via git workflow)
./scripts/git.sh feature db-changes
./scripts/git.sh commit "Add database migration: Description"
./scripts/git.sh finish-feature     # Auto-deploys to development with migration

# Deploy to production after testing (automatic)
./scripts/git.sh release            # Auto-deploys to production with migration
```

#### Manual Migration Deployment (Emergency Only)
**⚠️ Only use if automated deployment fails:**
```bash
# If automatic deployment fails, manual deployment
railway environment development
railway up

# For production
railway environment production
railway up
```

### Health Check Implementation

#### Health Check Endpoint
```python
@app.get("/healthz/")
def health_check_endpoint():
    """Health check endpoint for Railway deployment."""
    try:
        # Check database connectivity
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    return {
        "status": "ok",
        "database": db_status,
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "timestamp": datetime.utcnow().isoformat()
    }
```

#### Railway Health Check Configuration
For GitHub source deployment, create a `railway.json` file in your repository root:

```json
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "healthcheckPath": "/healthz/",
    "healthcheckTimeout": 300,
    "restartPolicyType": "on_failure",
    "startCommand": "gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT"
  }
}
```

### Monitoring and Logging

#### Application Logging Setup
```python
import logging
import os

# Configure logging based on environment
log_level = logging.DEBUG if os.getenv("ENVIRONMENT") == "development" else logging.INFO

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output for Railway
    ]
)

logger = logging.getLogger(__name__)
```

#### Error Tracking Patterns
```python
def log_api_error(endpoint: str, error: Exception, request_data: dict = None):
    """Centralized error logging for API endpoints."""
    error_context = {
        "endpoint": endpoint,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "request_data": request_data,
        "timestamp": datetime.utcnow().isoformat()
    }

    logger.error(f"API Error: {error_context}")

    # In production, could send to external monitoring service
    if os.getenv("ENVIRONMENT") == "production":
        # send_to_monitoring_service(error_context)
        pass
```

### Performance Optimization

#### Gunicorn Configuration
```bash
# Production gunicorn command
gunicorn main:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind "[::]:\${PORT:-8000}" \
    --timeout 120 \
    --keepalive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50
```

#### Database Connection Optimization
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

# Optimized database configuration
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    echo=False  # Set to True for development debugging
)
```

### Security Configuration

#### CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.raposa\.tech|https://raposa\.tech|https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

#### Environment-Based Security
```python
# Environment-aware documentation access
docs_url = "/docs" if os.getenv("ENVIRONMENT") == "development" else None
redoc_url = "/redoc" if os.getenv("ENVIRONMENT") == "development" else None

app = FastAPI(
    title="Raposa Domain Checker API",
    docs_url=docs_url,
    redoc_url=redoc_url
)
```

### Deployment Checklist

#### Pre-Deployment Verification
- [ ] Database migrations tested in development
- [ ] Environment variables configured correctly
- [ ] Health check endpoint responding
- [ ] Email templates rendering properly
- [ ] CORS configuration allows required origins
- [ ] Rate limiting working as expected
- [ ] Error handling tested

#### Post-Deployment Verification
- [ ] Health check endpoint accessible
- [ ] API endpoints responding correctly
- [ ] Database connectivity working
- [ ] Email sending functional
- [ ] Logs showing expected output
- [ ] Performance metrics within acceptable range

### Rollback Strategy

#### Quick Rollback Process (Recommended)
```bash
# Use the automated rollback script
./scripts/railway.sh rollback

# Verify rollback success
./scripts/railway.sh health
```

#### Manual Rollback Process (Emergency Only)
**⚠️ Only use if scripts fail:**
```bash
# Identify last good deployment
railway deployments

# Rollback to specific deployment
railway rollback <deployment-id>

# Verify rollback success
curl https://api.domainchecker.raposa.tech/healthz/
```

#### Database Rollback
```bash
# Rollback database migration if needed
alembic downgrade <revision>

# Redeploy application
railway up
```

Remember to always test deployments in the development environment before promoting to production.
