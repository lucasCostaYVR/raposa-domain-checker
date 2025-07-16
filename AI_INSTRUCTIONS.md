# AI Development Instructions for Raposa Domain Checker

## Project Context
This is a FastAPI-based domain security analysis tool that checks DNS records (MX, SPF, DKIM, DMARC) and provides security recommendations. The app is deployed on Railway with PostgreSQL databases.

## Current Architecture
```
src/
├── main.py          # FastAPI application and routes
├── models.py        # SQLAlchemy database models
├── schemas.py       # Pydantic request/response models
└── database.py      # Database configuration and sessions
```

## Development Principles

### 1. Code Style and Quality
- **Type Hints**: Always use type hints for function parameters and return values
- **Docstrings**: Include comprehensive docstrings for all public functions and classes
- **Error Handling**: Implement proper exception handling with meaningful error messages
- **Async/Await**: Use async operations for I/O-bound tasks (DNS queries, database operations)

### 2. FastAPI Best Practices
- **Dependency Injection**: Use FastAPI's dependency injection system for database sessions
- **Response Models**: Define Pydantic response models for all endpoints
- **Status Codes**: Use appropriate HTTP status codes (200, 201, 400, 404, 422, 500)
- **Request Validation**: Leverage Pydantic for automatic request validation
- **Documentation**: Ensure all endpoints have proper descriptions and examples

### 3. Database Operations
- **Migrations**: Always create Alembic migrations for schema changes
- **Sessions**: Use dependency injection for database sessions (`get_db()`)
- **Error Handling**: Handle database exceptions gracefully
- **Relationships**: Use SQLAlchemy relationships appropriately
- **Indexing**: Add indexes for frequently queried fields

### 4. DNS Operations
- **Timeout Handling**: Set reasonable timeouts for DNS queries (5-10 seconds)
- **Error Recovery**: Handle DNS resolution failures gracefully
- **Caching**: Consider caching DNS results with appropriate TTL
- **Multiple Queries**: Use asyncio for concurrent DNS queries when checking multiple records
- **Validation**: Validate domain names before making DNS queries

### 5. Security Considerations
- **Input Validation**: Sanitize and validate all user inputs
- **Domain Safety**: Ensure domains are safe to query (no internal/private domains)
- **Rate Limiting**: Implement rate limiting to prevent abuse
- **Data Privacy**: Minimize data collection and follow privacy best practices
- **SQL Injection**: Use parameterized queries (SQLAlchemy handles this)

### 6. Error Handling Patterns
```python
# Good error handling pattern
try:
    result = await dns_query(domain)
    return {"status": "success", "data": result}
except dns.exception.Timeout:
    raise HTTPException(status_code=408, detail="DNS query timeout")
except dns.exception.NXDOMAIN:
    raise HTTPException(status_code=404, detail="Domain not found")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

### 7. Logging Standards
```python
import logging
logger = logging.getLogger(__name__)

# Log important events
logger.info(f"Domain check requested for {domain} by {email}")
logger.warning(f"Rate limit exceeded for {email}")
logger.error(f"DNS query failed for {domain}: {error}")
```

### 8. Configuration Management
- Use Pydantic Settings for all configuration
- Environment variables for sensitive data
- Default values for development
- Validation for required settings

### 9. Testing Guidelines
- Write unit tests for business logic
- Test edge cases (invalid domains, timeout scenarios)
- Mock external dependencies (DNS queries)
- Test API endpoints with various inputs
- Include performance tests for critical paths

### 10. Performance Considerations
- Use async operations for I/O-bound tasks
- Implement connection pooling for databases
- Consider caching for frequently accessed data
- Monitor memory usage for large operations
- Set appropriate timeouts for external services

## File-Specific Guidelines

### main.py
- Keep routes clean and focused
- Use dependency injection for shared resources
- Implement proper error handling middleware
- Add comprehensive API documentation

### models.py
- Use appropriate column types and constraints
- Add indexes for frequently queried fields
- Include relationships between models
- Add validation at the model level

### schemas.py
- Define separate request and response models
- Use Field() for validation and documentation
- Include examples in schema definitions
- Validate email formats and domain names

### database.py
- Configure connection pooling appropriately
- Handle connection errors gracefully
- Use environment variables for database URLs
- Implement proper session management

## Common Patterns

### DNS Query Pattern
```python
import dns.resolver
import asyncio
from typing import Optional, Dict, Any

async def query_dns_record(domain: str, record_type: str, timeout: int = 5) -> Optional[Dict[str, Any]]:
    """Query DNS record with proper error handling."""
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout
        resolver.lifetime = timeout
        
        result = resolver.resolve(domain, record_type)
        return {"records": [str(record) for record in result]}
    except dns.exception.Timeout:
        logger.warning(f"DNS timeout for {domain} ({record_type})")
        return None
    except dns.exception.NXDOMAIN:
        logger.info(f"Domain not found: {domain}")
        return None
    except Exception as e:
        logger.error(f"DNS query error for {domain}: {e}")
        return None
```

### Database Operation Pattern
```python
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

async def create_domain_check(
    domain_data: DomainCheckCreate,
    db: Session = Depends(get_db)
) -> DomainCheck:
    """Create a new domain check with proper error handling."""
    try:
        db_check = DomainCheck(**domain_data.dict())
        db.add(db_check)
        db.commit()
        db.refresh(db_check)
        return db_check
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Domain check already exists")
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### API Endpoint Pattern
```python
@app.post("/check-domain", response_model=DomainCheckResponse)
async def check_domain(
    request: DomainCheckRequest,
    db: Session = Depends(get_db)
) -> DomainCheckResponse:
    """
    Check domain security configuration.
    
    - **domain**: Domain name to check (e.g., example.com)
    - **email**: Email address for results delivery
    """
    try:
        # Validate domain format
        if not is_valid_domain(request.domain):
            raise HTTPException(status_code=422, detail="Invalid domain format")
        
        # Check usage limits
        if await check_usage_limit(request.email, db):
            raise HTTPException(status_code=429, detail="Usage limit exceeded")
        
        # Perform domain check
        result = await perform_domain_check(request.domain)
        
        # Save to database
        db_check = await create_domain_check(request, result, db)
        
        return DomainCheckResponse.from_orm(db_check)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in check_domain: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Development Workflow

1. **Feature Development**:
   - Create feature branch from `develop`
   - Write tests first (TDD approach)
   - Implement feature with proper error handling
   - Update documentation and type hints
   - Test locally with `run_dev.sh`

2. **Database Changes**:
   - Update models in `models.py`
   - Create migration with `alembic revision --autogenerate -m "description"`
   - Test migration locally
   - Apply to development database

3. **API Changes**:
   - Update schemas in `schemas.py`
   - Update routes in `main.py`
   - Test with FastAPI docs at `/docs`
   - Update API documentation

4. **Deployment**:
   - Ensure all tests pass
   - Deploy to Railway development environment
   - Validate functionality
   - Deploy to production

## Debugging Guidelines

1. **Use structured logging** with correlation IDs
2. **Check Railway logs** for deployment issues
3. **Monitor database performance** with query analysis
4. **Test DNS queries manually** with dig/nslookup
5. **Use FastAPI docs** for API testing
6. **Check environment variables** in Railway dashboard

Remember: Always prioritize code readability, maintainability, and user experience. When in doubt, choose the simpler, more explicit approach.
