# Raposa Domain Checker API

A FastAPI-based application for checking domain DNS records including MX, SPF, DKIM, and DMARC records. Built for deployment on Railway with PostgreSQL database.

## Features

- ✅ Domain DNS record checking (MX, SPF, DKIM, DMARC)
- ✅ Usage limits (5 checks per domain per month)
- ✅ Email collection with optional marketing opt-in
- ✅ PostgreSQL database integration with Railway
- ✅ Database migrations with Alembic
- ✅ FastAPI with automatic OpenAPI documentation
- ✅ Separate development and production environments

## Development Setup

### Prerequisites

- Python 3.12+
- Railway CLI
- PostgreSQL databases setup on Railway

### Quick Start

1. **Clone and setup virtual environment:**
   ```bash
   git clone <repository>
   cd raposa-app
   python3 -m venv .venv
   source .venv/bin/activate  # or use the configured environment
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Railway databases:**
   - Development and production PostgreSQL databases are already configured
   - Use `railway environment development` for dev work
   - Use `railway environment production` for production

4. **Run database migrations:**
   ```bash
   railway run python -m alembic upgrade head
   ```

5. **Start development server:**
   ```bash
   ./run_dev.sh
   ```

   The development script will:
   - Kill any existing processes on port 8000
   - Switch to development environment
   - Start FastAPI server with hot reload

### API Endpoints

- **GET /** - API information
- **GET /healthz/** - Health check
- **POST /check-domain** - Check domain DNS records
- **GET /domain-usage/{domain}** - Check usage for a domain

### API Documentation

When running the development server, visit:
- **Interactive API docs:** http://localhost:8000/docs
- **ReDoc documentation:** http://localhost:8000/redoc

### Testing

Run the test script to verify all endpoints:
```bash
./test_api.sh
```

## Project Structure

```
raposa-app/
├── src/
│   ├── main.py          # FastAPI application
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic request/response models
│   └── database.py      # Database configuration
├── alembic/             # Database migrations
├── requirements.txt     # Python dependencies
├── run_dev.sh          # Development server script
├── test_api.sh         # API testing script
├── railway.json        # Railway deployment config
└── Dockerfile          # Container configuration
```

## Database Schema

### Tables

**domain_checks:**
- Stores each domain check with results
- Includes MX, SPF, DKIM, DMARC records
- Tracks email, opt-in status, and timestamps

**domain_usage:**
- Tracks monthly usage per domain
- Enforces 5-check limit per domain per month

## Railway Setup Summary

### Databases Created:
- **Development Environment:** Postgres-1Be3 database
- **Production Environment:** Postgres database

### Connection Details:
- Use `DATABASE_PUBLIC_URL` for external connections (local development)
- Use `DATABASE_URL` for internal Railway connections (deployed app)

## Deployment

The application is configured for Railway deployment with:
- PostgreSQL databases (development & production)
- Environment-based configuration
- Health check endpoints
- Docker containerization

## Environment Variables

- `DATABASE_URL` - Internal database connection
- `DATABASE_PUBLIC_URL` - External database connection (for local development)

## Next Steps

1. ✅ ~~Setup basic API and database~~
2. ✅ ~~Deploy to Railway for testing~~
3. 🔄 Enhance DNS checking logic
4. 🔄 Improve scoring algorithm
5. 🔄 Add detailed recommendations
6. 🔄 Implement email reporting
7. 🔄 Build frontend interface

Includes:

- Minimal FastAPI app
- FastAPI-built Dockerfile for continuous deployments
- Endpoint for deployment health checks during Railway deploys

Code: https://github.com/jmitchel3/fastapi-container
Railway Template: https://fastapicontainer.com
Reference blog post on [Coding for Entrepreneurs](https://www.codingforentrepreneurs.com/blog/deploy-fastapi-to-railway-with-this-dockerfile)