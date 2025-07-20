# FastAPI Railway Starter

A production-ready FastAPI application template with PostgreSQL, Railway deployment, and essential features for rapid API development.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

1. **Clone this repository:**
   ```bash
   git clone <your-repo-url>
   cd fastapi-railway-starter
   ```

2. **Run the automated setup:**
   ```bash
   ./setup_railway.sh
   ```

This script will:
- Create a new Railway project
- Add PostgreSQL database
- Configure environment variables
- Set up deployment configuration
- Deploy your API

### Option 2: Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Railway:**
   ```bash
   railway login
   railway project new your-project-name
   railway add postgresql
   railway link
   ```

3. **Deploy:**
   ```bash
   railway up
   ```

## 📁 Project Structure

```
├── main.py                 # FastAPI application entry point
├── src/
│   ├── database.py         # Database configuration
│   ├── models.py           # SQLAlchemy models (add your models here)
│   └── schemas.py          # Pydantic schemas (add your schemas here)
├── alembic/                # Database migrations
├── requirements.txt        # Python dependencies
├── railway.json           # Railway deployment config
├── setup_railway.sh       # Automated setup script
└── README.md              # This file
```

## 🛠️ Features

### ✅ Included
- **FastAPI** with automatic API documentation
- **PostgreSQL** database with SQLAlchemy ORM
- **Alembic** for database migrations
- **Railway** deployment configuration
- **Environment-based configuration** (development vs production)
- **Health check endpoint** (`/health/`)
- **CORS middleware** configured
- **Global exception handling**
- **Structured logging**
- **Production-ready gunicorn configuration**

### 🔧 Ready to Add
- Authentication/authorization
- Email services
- Background tasks
- File uploads
- Rate limiting
- Caching
- Testing setup

## 📊 API Endpoints

- `GET /health/` - Health check endpoint
- `GET /docs` - Interactive API documentation (development only)
- `GET /redoc` - Alternative API documentation (development only)

## 🗄️ Database

### Models
Add your SQLAlchemy models to `src/models.py`:

```python
from src.models import Base
from sqlalchemy import Column, Integer, String, DateTime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Migrations
Create and apply database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "Add user model"

# Apply migrations
alembic upgrade head
```

### Schemas
Add your Pydantic schemas to `src/schemas.py`:

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
```

## 🌐 Adding API Endpoints

Add your endpoints to `main.py`:

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas import UserCreate, UserResponse

@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Your endpoint logic here
    pass
```

## 🏗️ Development

### Local Development
1. **Set up local database:**
   ```bash
   # Install PostgreSQL locally or use Docker
   docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres
   ```

2. **Update `.env` file:**
   ```bash
   ENVIRONMENT=development
   DATABASE_URL=postgresql://postgres:password@localhost:5432/your_db
   ```

3. **Run the application:**
   ```bash
   python -m uvicorn main:app --reload --port 8000
   ```

4. **Access the API:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health/

### Railway Commands
```bash
# View logs
railway logs

# Check status
railway status

# Open shell in production
railway shell

# Deploy changes
railway up

# Set environment variables
railway variables set KEY=value
```

## 🔧 Configuration

### Environment Variables
- `ENVIRONMENT` - Set to "development" or "production"
- `DATABASE_URL` - PostgreSQL connection string (auto-set by Railway)
- `PORT` - Application port (auto-set by Railway)

### CORS Configuration
Update CORS origins in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com", "https://www.yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## 📦 Adding Dependencies

1. **Add to requirements.txt:**
   ```bash
   echo "new-package==1.0.0" >> requirements.txt
   ```

2. **Install locally:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Deploy changes:**
   ```bash
   railway up
   ```

## 🚀 Deployment

### Automatic Deployment
Connect your GitHub repository in Railway dashboard for automatic deployments on push.

### Manual Deployment
```bash
railway up
```

### Health Checks
Railway uses `/health/` endpoint for health monitoring with 120-second timeout.

## 🔍 Monitoring

### Health Check
```bash
curl https://your-app.railway.app/health/
```

### Logs
```bash
railway logs --follow
```

## 🧪 Testing

Add testing dependencies to `requirements.txt`:
```
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

Create tests in `tests/` directory:
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

- [Railway Documentation](https://docs.railway.app/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

**Happy coding! 🎉**
