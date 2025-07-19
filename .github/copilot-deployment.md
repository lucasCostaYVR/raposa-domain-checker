# Deployment and Infrastructure Instructions

## Railway Deployment Patterns

### Docker Configuration

#### Dockerfile Best Practices
```dockerfile
# Use specific Python version for consistency
FROM python:3.12-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    libjpeg-dev \
    libcairo2 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --upgrade pip
RUN mkdir -p /code
WORKDIR /code

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

#### Railway Environment Configuration
```bash
# Set environment variables in Railway
railway variables set ENVIRONMENT=production
railway variables set DATABASE_URL=${{ Postgres.DATABASE_URL }}
railway variables set SENDGRID_API_KEY=your_api_key
railway variables set SENDGRID_FROM_EMAIL=noreply@raposa.tech
```

### Branch-Based Deployment Strategy

#### Production Deployment (main branch)
```bash
# Switch to main branch
git checkout main

# Link to production environment
railway environment production
railway service raposa-app-api

# Deploy to production
railway up
```

#### Development Deployment (develop branch)
```bash
# Switch to develop branch
git checkout develop

# Link to development environment
railway environment development
railway service raposa-stage

# Deploy to staging
railway up
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
```bash
# Generate migration locally
alembic revision --autogenerate -m "Description of changes"

# Test migration on development
git checkout develop
railway environment development
railway up

# Deploy to production after testing
git checkout main
git merge develop
git push origin main
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
```toml
# railway.json
{
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "healthcheckPath": "/healthz/",
    "healthcheckTimeout": 300,
    "restartPolicyType": "on_failure"
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

#### Quick Rollback Process
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
