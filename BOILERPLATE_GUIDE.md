# 🚀 FastAPI Railway Boilerplate - Complete Usage Guide

> A production-ready FastAPI boilerplate with automated Railway deployment, multi-environment support, and comprehensive development tools.

## 🎯 Quick Start

### 1. Clone and Setup
```bash
# Clone the boilerplate
git clone <your-boilerplate-repo>
cd your-new-project

# Setup development environment
./scripts/dev.sh setup

# Start local development
./scripts/dev.sh start
```

### 2. Deploy to Railway (One Command!)
```bash
./setup_railway.sh
```
Choose your environments:
- **Option 1**: Production only
- **Option 2**: Staging + Production (recommended)

## 📁 Project Structure

```
your-project/
├── main.py                 # FastAPI application entry point
├── database.py             # Database configuration & session management
├── models.py               # SQLAlchemy database models
├── schemas.py              # Pydantic request/response schemas
├── requirements.txt        # Python dependencies
├── railway.json           # Railway deployment configuration
├── alembic.ini            # Database migration configuration
├── alembic/               # Migration files
├── scripts/               # Development automation
│   ├── dev.sh            # Local development tools
│   ├── railway.sh        # Railway management
│   └── git.sh           # Git workflow helpers
└── setup_railway.sh      # One-command Railway setup
```

**Key Design Decisions:**
- ✅ **Flat structure**: All Python modules in root for clean imports
- ✅ **No src/ folder**: Prevents deployment import issues
- ✅ **Railway-first**: Optimized for Railway deployment
- ✅ **Script automation**: Everything automated with beautiful CLI

## 🛠️ Development Workflow

### Daily Development
```bash
# Start development server with hot reload
./scripts/dev.sh start

# Test your API
./scripts/dev.sh test

# Format code
./scripts/dev.sh format

# Install new package
./scripts/dev.sh install fastapi-users
```

### Database Operations
```bash
# Create new migration
./scripts/dev.sh migrate "Add user table"

# Apply migrations locally
./scripts/dev.sh db-upgrade

# Reset database (careful!)
./scripts/dev.sh db-reset
```

### Git Workflow
```bash
# Quick status check
./scripts/git.sh status

# Create feature branch
./scripts/git.sh feature user-authentication

# Quick commit
./scripts/git.sh commit "Add user model"

# Push changes
./scripts/git.sh push
```

### Railway Management
```bash
# Deploy to Railway
./scripts/railway.sh deploy

# Check status
./scripts/railway.sh status

# View logs
./scripts/railway.sh logs

# Open Railway dashboard
./scripts/railway.sh dashboard
```

## 🏗️ Adding Features

### 1. Create Database Model
```python
# models.py
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
```

### 2. Create Pydantic Schemas
```python
# schemas.py
class UserCreateRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True
```

### 3. Add API Endpoints
```python
# main.py
from models import User
from schemas import UserCreateRequest, UserResponse

@app.post("/users", response_model=UserResponse)
async def create_user(
    user: UserCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new user."""
    db_user = User(
        email=user.email,
        username=user.username
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### 4. Create Migration & Deploy
```bash
# Create migration
./scripts/dev.sh migrate "Add user table"

# Test locally
./scripts/dev.sh start

# Deploy to staging
./scripts/railway.sh deploy --env staging

# Deploy to production
./scripts/railway.sh deploy --env production
```

## 🌍 Multi-Environment Setup

The boilerplate supports staging and production environments:

### Environment Structure
```
Railway Project: your-project
├── Staging Environment
│   ├── your-project-python-stage  # FastAPI service
│   └── Postgres                   # Database
└── Production Environment
    ├── your-project-python        # FastAPI service
    └── Postgres                   # Database
```

### Environment Variables
```bash
# Staging
DATABASE_URL=postgresql://...     # Auto-configured by Railway
ENVIRONMENT=staging               # Auto-set by Railway

# Production  
DATABASE_URL=postgresql://...     # Auto-configured by Railway
ENVIRONMENT=production            # Auto-set by Railway
```

### Deployment Strategy
```bash
# Deploy to staging first
railway environment staging
railway up

# Test staging deployment
curl https://your-project-python-stage.up.railway.app/health/

# Deploy to production
railway environment production
railway up
```

## 🤖 AI Assistant Instructions

### For GitHub Copilot / AI Development

**Project Context:**
- This is a **FastAPI boilerplate** for rapid API development
- Uses **flat project structure** (no src/ folder)
- Optimized for **Railway deployment**
- All automation via **scripts in ./scripts/**

**Code Style:**
```python
# ✅ Correct imports (flat structure)
from database import get_db, engine
from schemas import UserResponse
from models import User

# ❌ Avoid (old src/ structure)
from src.database import get_db
from src.schemas import UserResponse
```

**Development Commands:**
```bash
# ✅ Use project scripts
./scripts/dev.sh start        # Start development
./scripts/dev.sh migrate "..."  # Create migration
./scripts/railway.sh deploy   # Deploy to Railway

# ❌ Avoid manual commands
uvicorn main:app --reload     # Use script instead
alembic revision --autogenerate  # Use script instead
```

**When Adding Features:**
1. **Models first**: Add to `models.py`
2. **Schemas next**: Add to `schemas.py` 
3. **Endpoints last**: Add to `main.py`
4. **Migration**: `./scripts/dev.sh migrate "Description"`
5. **Test**: `./scripts/dev.sh test`
6. **Deploy**: `./scripts/railway.sh deploy`

**Railway Patterns:**
- Project naming: `project-name-python` (production), `project-name-python-stage` (staging)
- Environment variables: Auto-configured DATABASE_URL
- Health checks: Always use `/health/` endpoint
- Logs: Use `./scripts/railway.sh logs`

### For AI Code Generation

**API Endpoint Pattern:**
```python
@app.post("/endpoint", response_model=ResponseSchema)
async def endpoint_function(
    request: RequestSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Comprehensive docstring describing the endpoint.
    
    - **param**: Parameter description
    
    Returns detailed response description.
    """
    try:
        # Input validation
        # Business logic
        # Database operations
        # Background tasks if needed
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in endpoint_function: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

**Database Model Pattern:**
```python
class ModelName(Base):
    __tablename__ = "table_name"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add indexes for frequently queried fields
    # Add constraints for data integrity
    # Use proper column types and lengths
```

**Schema Pattern:**
```python
class RequestSchema(BaseModel):
    field: str = Field(..., description="Field description", max_length=255)
    
class ResponseSchema(BaseModel):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing: `./scripts/dev.sh test`
- [ ] Code formatted: `./scripts/dev.sh format`
- [ ] Migration created: `./scripts/dev.sh migrate "..."`
- [ ] Local testing complete: `./scripts/dev.sh start`

### Staging Deployment
- [ ] Deploy to staging: `./scripts/railway.sh deploy --env staging`
- [ ] Health check: `curl https://your-project-stage.up.railway.app/health/`
- [ ] Test new features on staging
- [ ] Database migration applied successfully

### Production Deployment
- [ ] Staging tests passed
- [ ] Deploy to production: `./scripts/railway.sh deploy --env production`
- [ ] Health check: `curl https://your-project.up.railway.app/health/`
- [ ] Monitor logs: `./scripts/railway.sh logs`
- [ ] Verify database connectivity

## 🔧 Customization

### Add Environment Variables
```bash
# Local development (.env)
API_KEY=your-secret-key
REDIS_URL=redis://localhost:6379

# Railway deployment
railway variables --set API_KEY=your-secret-key
railway variables --set REDIS_URL=...
```

### Add Dependencies
```bash
# Install and add to requirements.txt
./scripts/dev.sh install redis fastapi-cache

# Deploy with new dependencies
./scripts/railway.sh deploy
```

### Custom Scripts
```bash
# Add to scripts/ directory
cp scripts/dev.sh scripts/custom.sh
# Modify for your needs
```

## 📚 Resources

- **Railway Docs**: https://docs.railway.app/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Alembic Docs**: https://alembic.sqlalchemy.org/

## 🆘 Troubleshooting

### Common Issues

**Import Errors:**
```bash
# ❌ ImportError: cannot import name 'X' from 'Y'
# ✅ Solution: Use flat imports
from database import get_db  # not from src.database
```

**Railway Deployment Failed:**
```bash
# Check logs
./scripts/railway.sh logs

# Verify health endpoint
curl https://your-app.railway.app/health/

# Check environment variables
railway variables
```

**Database Connection Issues:**
```bash
# Verify DATABASE_URL is set
railway variables | grep DATABASE_URL

# Check database status
./scripts/railway.sh db
```

**Migration Issues:**
```bash
# Reset migrations locally
./scripts/dev.sh db-reset

# Recreate migration
./scripts/dev.sh migrate "Fresh migration"
```

---

## 🎉 Success!

You now have a production-ready FastAPI boilerplate with:
- ✅ Automated Railway deployment
- ✅ Multi-environment support
- ✅ Database integration
- ✅ Migration system
- ✅ Development automation
- ✅ Beautiful CLI tools

**Happy coding!** 🚀
