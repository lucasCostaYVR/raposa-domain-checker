# API Development Instructions

## FastAPI Best Practices for Raposa Domain Checker

### Endpoint Development Pattern
When creating new API endpoints, follow this structure:

```python
@app.{method}("/{path}", response_model={ResponseModel})
async def {function_name}(
    {request_params},
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Brief description of what this endpoint does.
    
    - **param1**: Description of parameter
    - **param2**: Description of parameter
    
    Returns: Description of return value and structure.
    """
    try:
        # 1. Input validation
        ensure_database_ready()
        
        # 2. Business logic validation
        if not await validation_function(input):
            raise HTTPException(status_code=422, detail="Validation error message")
        
        # 3. Database operations
        result = db.query(Model).filter(...).first()
        
        # 4. Business logic processing
        processed_data = await process_data(result)
        
        # 5. Database updates
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        
        # 6. Background tasks (if needed)
        background_tasks.add_task(background_function, params)
        
        # 7. Return response
        return processed_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in {function_name}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Request/Response Model Patterns

#### Request Models
```python
class {Operation}Request(BaseModel):
    field1: str = Field(..., description="Field description")
    field2: EmailStr = Field(..., description="Email validation")
    optional_field: Optional[bool] = Field(False, description="Optional field")
    
    @validator('field1')
    def validate_field1(cls, v):
        # Custom validation logic
        return v
```

#### Response Models
```python
class {Operation}Response(BaseModel):
    id: int
    status: str
    data: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### Database Interaction Patterns

#### Querying with Error Handling
```python
def get_domain_data(db: Session, domain: str) -> Optional[DomainCheck]:
    try:
        return db.query(DomainCheck).filter(
            DomainCheck.domain == domain
        ).first()
    except Exception as e:
        logger.error(f"Database query failed for domain {domain}: {e}")
        raise HTTPException(status_code=503, detail="Database service unavailable")
```

#### Creating Records
```python
def create_domain_check(db: Session, check_data: dict) -> DomainCheck:
    try:
        db_check = DomainCheck(**check_data)
        db.add(db_check)
        db.commit()
        db.refresh(db_check)
        return db_check
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create domain check: {e}")
        raise HTTPException(status_code=500, detail="Failed to save domain check")
```

### Background Task Patterns

#### Email Sending Tasks
```python
async def send_notification_email(email: str, subject: str, template_data: dict):
    """Background task for sending notification emails."""
    try:
        email_service = get_email_service()
        success = await email_service.send_template_email(
            to_email=email,
            subject=subject,
            template_name="notification",
            template_data=template_data
        )
        
        if success:
            logger.info(f"Notification email sent to {email}")
        else:
            logger.error(f"Failed to send notification email to {email}")
            
    except Exception as e:
        logger.error(f"Background email task failed: {e}")
```

### Validation Patterns

#### Domain Validation
```python
async def validate_domain_input(domain: str) -> bool:
    """Validate domain format and safety."""
    # Basic format validation
    if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
        return False
    
    # Security checks
    if any(domain.startswith(private) for private in PRIVATE_DOMAINS):
        return False
    
    return True
```

#### Rate Limiting
```python
def check_rate_limit(db: Session, identifier: str, limit: int, period: str) -> bool:
    """Check if operation is within rate limits."""
    current_period = datetime.now().strftime(f"%Y-{period}")
    
    usage = db.query(UsageModel).filter(
        UsageModel.identifier == identifier,
        UsageModel.period == current_period
    ).first()
    
    return not (usage and usage.count >= limit)
```

### Error Handling Guidelines

#### HTTP Exception Mapping
- `400`: Bad Request - Invalid input format
- `422`: Unprocessable Entity - Validation errors
- `429`: Too Many Requests - Rate limiting
- `500`: Internal Server Error - Unexpected errors
- `503`: Service Unavailable - Database/external service issues

#### Logging Best Practices
```python
# Info level for successful operations
logger.info(f"Domain check completed for {domain} - Score: {score}")

# Warning level for recoverable issues
logger.warning(f"Database retry attempt {attempt} for {operation}")

# Error level for failures
logger.error(f"Failed to process {operation}: {error_details}")
```

### API Documentation Standards

#### Endpoint Documentation
```python
@app.post("/check-domain", response_model=DomainCheckResponse)
async def check_domain(...):
    """
    Perform comprehensive domain security analysis.
    
    This endpoint analyzes domain DNS records including MX, SPF, DKIM, 
    and DMARC configurations, providing a security score and recommendations.
    
    **Rate Limiting**: 5 checks per domain per month
    
    **Parameters:**
    - **domain**: Domain name to analyze (e.g., example.com)
    - **email**: Email address for results delivery
    - **opt_in_marketing**: Whether to receive marketing communications
    
    **Returns:**
    - Comprehensive security analysis with scoring
    - DNS record details and validation results
    - Security recommendations and issue identification
    
    **Example Response:**
    ```json
    {
        "domain": "example.com",
        "score": 85,
        "grade": "B+",
        "mx_record": {...},
        "recommendations": [...]
    }
    ```
    """
```

### Testing Considerations

#### Unit Test Structure
```python
def test_domain_validation():
    # Valid cases
    assert await is_valid_domain("example.com") == True
    
    # Invalid cases
    assert await is_valid_domain("localhost") == False
    assert await is_valid_domain("invalid..domain") == False
```

#### Integration Test Pattern
```python
def test_check_domain_endpoint(client, db_session):
    response = client.post("/check-domain", json={
        "domain": "test.com",
        "email": "test@example.com",
        "opt_in_marketing": False
    })
    
    assert response.status_code == 200
    assert response.json()["domain"] == "test.com"
```

Remember to maintain consistency with existing code patterns and prioritize security, performance, and maintainability in all API development.
