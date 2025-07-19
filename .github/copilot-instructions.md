# GitHub Copilot Instructions for Raposa Domain Checker

## AI Assistant Guidelines
- **Be brief and direct**: Provide concise, actionable responses without unnecessary explanation
- **Prioritize scripts**: Always recommend project scripts over manual commands
- **Update documentation**: When making changes, update these instruction files to keep them current
- **Stay focused**: Address the specific request without verbose context

## Project Overview
This is a FastAPI-based domain security analysis API that provides comprehensive DNS record checking including MX, SPF, DKIM, and DMARC validation with intelligent scoring and email reporting capabilities.

## Technology Stack
- **Backend**: FastAPI (Python 3.12)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Email Service**: SendGrid with Jinja2 templating
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
- Use background tasks for email sending

### Database Patterns
- Use SQLAlchemy declarative models
- Implement proper session management
- Use database transactions for multi-table operations
- Handle database connection failures gracefully

## Project Structure
```
src/
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration and session management
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic request/response models
├── dns_utils.py         # DNS record checking utilities
├── email_service.py     # Email sending service with templates
└── templates/           # Jinja2 email templates
    ├── domain_report.html
    ├── domain_report.txt
    └── welcome_email.html
```

## Key Components

### Environment Configuration
- Development mode: `ENVIRONMENT=development` (enables /docs, uses create_all)
- Production mode: Uses Alembic migrations, disables documentation endpoints
- Environment-aware database setup with fallback mechanisms

### Email System
- Professional Jinja2 templates following brand guidelines
- SendGrid integration for reliable delivery
- Background task processing for non-blocking email sending
- Welcome emails for first-time users

### Database Management
- Environment-aware setup (development vs production)
- Automatic migration handling in production
- Graceful fallback to create_all if migrations fail
- Retry logic for database connection issues

## Development Scripts

The project includes comprehensive helper scripts in the `scripts/` directory for streamlined development and deployment workflows:

### Railway Management (`scripts/railway.sh`)
```bash
# Deploy to environments
./scripts/railway.sh deploy-dev      # Deploy to development
./scripts/railway.sh deploy-prod     # Deploy to production
./scripts/railway.sh health          # Check API health for both environments
./scripts/railway.sh switch dev/prod # Switch between environments
./scripts/railway.sh logs            # View current environment logs
./scripts/railway.sh rollback        # Emergency rollback
./scripts/railway.sh migrate "msg"   # Create database migration
```

### Development Tools (`scripts/dev.sh`)
```bash
# Local development
./scripts/dev.sh start              # Start development server with hot reload
./scripts/dev.sh setup              # Setup complete development environment
./scripts/dev.sh test               # Test API endpoints locally
./scripts/dev.sh format             # Format code with Black
./scripts/dev.sh lint               # Lint code with flake8
./scripts/dev.sh tests              # Run test suite
./scripts/dev.sh session            # Full development startup workflow
```

### Git Workflow (`scripts/git.sh`)
```bash
# Feature development workflow
./scripts/git.sh feature <name>     # Start new feature branch
./scripts/git.sh commit "message"   # Quick commit with proper formatting
./scripts/git.sh finish-feature     # Merge feature to develop (auto-deploys)
./scripts/git.sh release            # Release develop to main (production)
./scripts/git.sh status             # Comprehensive git status
./scripts/git.sh sync               # Sync with remote safely
```

### Environment Setup (`scripts/setup.sh`)
```bash
# One-command setup for new developers
./scripts/setup.sh                  # Complete development environment setup
```

**Always use these scripts** instead of manual commands for:
- Deployments (use railway.sh instead of manual Railway CLI)
- Environment switching (automated safety checks)
- Feature development (proper branch workflow)
- Code formatting and testing (consistent standards)

## Development Guidelines

### Adding New Features
1. Create Pydantic schemas for request/response models
2. Implement database models with proper relationships
3. Add comprehensive error handling
4. Include background tasks for async operations
5. Write descriptive docstrings and type hints

### Database Changes
1. Create Alembic migrations for schema changes
2. Test migrations in development environment first
3. Ensure backward compatibility when possible
4. Update models.py to reflect schema changes

### Email Templates
1. Follow brand guidelines in templates/
2. Include both HTML and plain text versions
3. Use Jinja2 templating for dynamic content
4. Test email rendering before deployment

### Error Handling
- Use HTTPException for API errors
- Log errors with appropriate severity levels
- Provide user-friendly error messages
- Implement retry logic for transient failures

## Deployment Strategy

### Branch Strategy
- `main` branch → Production environment (`api.domainchecker.raposa.tech`)
- `develop` branch → Development environment (`stage.domainchecker.raposa.tech`)

### Railway Deployment
- Docker-based deployment using Dockerfile
- Automatic deployments on branch pushes
- Environment-specific configuration
- Health checks at `/healthz/` endpoint

## Testing Guidelines
- Test API endpoints with various input scenarios
- Validate email template rendering
- Test database migration scenarios
- Verify DNS record parsing accuracy

## Security Considerations
- Validate domain input to prevent injection attacks
- Rate limiting on domain checks (5 per domain per month)
- CORS configuration for trusted origins only
- Environment-based security settings

## Common Patterns to Follow

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

### Email Service Pattern
```python
async def send_email_function(self, to_email: str, **template_data):
    """Send email with template rendering."""
    try:
        template_data = self._prepare_template_data(**template_data)
        # Template rendering and email sending logic
        return True
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        return False
```

## Documentation Maintenance

### Keeping Instructions Current
- **Always update these instruction files** when making significant changes to:
  - Project structure or architecture
  - Development workflows or scripts
  - Deployment processes or environments
  - Code patterns or conventions
  - New features or major refactoring

### Files to Update
- `copilot-instructions.md` - Main project overview and guidelines
- `copilot-api-instructions.md` - FastAPI patterns and endpoint development
- `copilot-database-email.md` - Database and email service patterns
- `copilot-deployment.md` - Infrastructure and deployment workflows
- `copilot-dns-analysis.md` - DNS analysis and scoring patterns
- `copilot-scripts.md` - Development script documentation

### Update Process
```bash
# When making changes that affect documentation
./scripts/git.sh commit "Update feature and documentation"
# Always mention documentation updates in commit messages
```

Remember to maintain consistency with existing patterns and prioritize code readability and maintainability.
