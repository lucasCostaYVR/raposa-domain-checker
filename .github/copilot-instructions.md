# GitHub Copilot Instructions for FastAPI Boilerplate

## AI Assistant Guidelines
- **Be brief and direct**: Provide concise, actionable responses without unnecessary explanation
- **Prioritize scripts**: Always recommend project scripts over manual commands
- **Update documentation**: When making changes, update these instruction files to keep them current
- **Stay focused**: Address the specific request without verbose context

## Project Overview
This is a clean FastAPI boilerplate for rapid API development. It provides a minimal foundation with database integration, Railway deployment automation, and development tooling for building modern APIs quickly.

## Technology Stack
- **Backend**: FastAPI (Python 3.12+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Deployment**: Railway (Docker-based)
- **Environment Management**: python-dotenv

## Code Style & Conventions

### Python Style
- Follow PEP 8 standards
- Use type hints for all function parameters and return values
- Prefer async/await for I/O operations
- Use descriptive variable names and docstrings
- Maximum line length: 88 characters (Black formatter)

### FastAPI Patterns
- Use dependency injection with `Depends()`
- Implement proper exception handling with HTTPException
- Use Pydantic models for request/response validation
- Include comprehensive docstrings for API endpoints
- Use background tasks for async operations

### Database Patterns
- **PostgreSQL only**: Use PostgreSQL for all environments (development, staging, production)
- Use SQLAlchemy declarative models
- Implement proper session management
- Use database transactions for multi-table operations
- Handle database connection failures gracefully

## Project Structure
```
main.py                  # FastAPI application entry point (project root)
database.py              # Database configuration and session management
models.py                # SQLAlchemy database models (examples in comments)
schemas.py               # Pydantic request/response models (examples in comments)
requirements.txt         # Python dependencies
railway.json             # Railway deployment configuration
alembic.ini              # Alembic migration configuration
alembic/                 # Database migration files
scripts/                 # Development automation scripts
├── dev.sh              # Development helper commands
├── railway.sh          # Railway deployment management
└── git.sh              # Git workflow automation
setup_railway.sh         # One-command Railway project setup
```

**Important**: All Python modules are in the project root for simplified imports. No `src/` directory - this ensures Railway deployment compatibility and cleaner import statements.

## Development Scripts

The boilerplate includes comprehensive helper scripts for streamlined development:

### Development Tools (`scripts/dev.sh`)
```bash
# Local development
./scripts/dev.sh start              # Start development server with hot reload
./scripts/dev.sh setup              # Setup development environment
./scripts/dev.sh test               # Test API endpoints
./scripts/dev.sh migrate "message"  # Create database migration
./scripts/dev.sh shell              # Open Python shell with app context
./scripts/dev.sh format             # Format code with Black
./scripts/dev.sh lint               # Lint code with flake8
./scripts/dev.sh install <package>  # Install Python package
./scripts/dev.sh clean              # Clean cache and temp files
```

### Railway Management (`scripts/railway.sh`)
```bash
# Railway operations
./scripts/railway.sh status         # Show project status
./scripts/railway.sh deploy         # Deploy to Railway
./scripts/railway.sh logs           # View application logs
./scripts/railway.sh shell          # Open production shell
./scripts/railway.sh env            # Manage environment variables
./scripts/railway.sh db             # Database operations
./scripts/railway.sh health         # Check API health
./scripts/railway.sh setup          # Setup new Railway project
```

### Git Workflow (`scripts/git.sh`)
```bash
# Git operations
./scripts/git.sh status             # Comprehensive git status
./scripts/git.sh sync               # Sync with remote safely
./scripts/git.sh feature <name>     # Create feature branch
./scripts/git.sh commit "message"   # Quick commit
./scripts/git.sh push               # Push current branch
./scripts/git.sh cleanup            # Clean up merged branches
./scripts/git.sh log                # Show recent commits
```

### Initial Setup (`setup_railway.sh`)
```bash
# One-command Railway setup
./setup_railway.sh                  # Complete Railway project setup
```

**Always use these scripts** instead of manual commands for consistency and automation.

## Quick Start Guide

### 1. Setup New Project
```bash
# Clone/copy the boilerplate
git clone <your-boilerplate-repo>
cd your-new-project

# Setup development environment
./scripts/dev.sh setup

# Setup Railway deployment (optional)
./setup_railway.sh
```

### 2. Add Your API Logic
```bash
# Start development server
./scripts/dev.sh start

# Edit src/models.py for database models
# Edit src/schemas.py for request/response models
# Edit main.py for API endpoints
```

### 3. Database Setup
```bash
# Create migration for your models
./scripts/dev.sh migrate "Add your models"

# Deploy with migrations
./scripts/railway.sh deploy
```

## Development Guidelines

### Adding New Features
1. Create Pydantic schemas in `schemas.py`
2. Implement database models in `models.py`
3. Add API endpoints in `main.py`
4. Create database migrations with `./scripts/dev.sh migrate`
5. Test locally with `./scripts/dev.sh test`

### Database Changes
1. Modify models in `models.py`
2. Create migration: `./scripts/dev.sh migrate "Description"`
3. Test migration locally
4. Deploy: `./scripts/railway.sh deploy`

### Error Handling
- Use HTTPException for API errors
- Log errors with appropriate severity levels
- Provide user-friendly error messages
- Implement retry logic for transient failures

## Deployment Strategy

### Railway Deployment
- **nixpacks-based deployment**: Auto-detection for Python projects
- **No Dockerfile required**: Uses nixpacks auto-detection
- **Automatic PostgreSQL**: Added via Railway services
- **Environment-specific configuration**: Uses railway.json
- **Health checks**: `/health/` endpoint with timeout
- **Import structure**: main.py in project root with `from src.module` imports

### Railway Configuration (railway.json)
```json
{
    "build": {
        "builder": "nixpacks"
    },
    "deploy": {
        "healthcheckPath": "/health/",
        "healthcheckTimeout": 120,
        "restartPolicyType": "ON_FAILURE",
        "startCommand": "gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 --keep-alive 5"
    }
}
```

### Critical Deployment Notes
- **Use nixpacks auto-detection**: No custom configuration needed
- **Health check requirements**: Must use proper SQLAlchemy imports
- **Import pattern**: All imports from project modules use simple imports like `from database import engine, get_db`
- **Startup command**: Use `gunicorn main:app` (main.py in root)

## Testing Guidelines
- Test API endpoints with various input scenarios
- Validate database operations
- Test deployment and health checks
- Use automated testing in CI/CD

## Security Considerations
- Validate all input to prevent injection attacks
- Use environment variables for sensitive data
- Implement proper CORS configuration
- Use HTTPS in production

## Common Patterns

### API Endpoint Structure
```python
@app.post("/endpoint", response_model=ResponseModel)
async def endpoint_function(
    request: RequestModel,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Comprehensive docstring describing the endpoint.

    - **param**: Parameter description

    Returns detailed response description.
    """
    try:
        # Validation logic
        # Business logic
        # Database operations
        # Background task scheduling
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error description: {e}")
        raise HTTPException(status_code=500, detail="User-friendly error message")
```

### Database Model Pattern
```python
class ModelName(Base):
    __tablename__ = "table_name"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Additional fields with proper types and constraints
```

### Pydantic Schema Pattern
```python
class RequestModel(BaseModel):
    field: str = Field(..., description="Field description")

class ResponseModel(BaseModel):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
```

## Customization Guide

### Environment Variables
Add to Railway or local `.env`:
```
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
ENVIRONMENT=development|production
```

### Adding New Dependencies
```bash
# Install package
./scripts/dev.sh install package-name

# Update requirements.txt automatically handled
```

### Database Migrations
```bash
# Create migration
./scripts/dev.sh migrate "Add new table"

# Apply migrations (auto in production)
alembic upgrade head
```

## Documentation Maintenance

### Keeping Instructions Current
Update this file when making significant changes to:
- Project structure or architecture
- Development workflows or scripts
- Deployment processes
- Code patterns or conventions

### Update Process
```bash
# When making changes
./scripts/git.sh commit "Update feature and documentation"
```

Remember to maintain consistency with existing patterns and prioritize code readability and maintainability.
