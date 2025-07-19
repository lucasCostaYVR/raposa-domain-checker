# Database and Email Service Instructions

## Database Development Patterns

### SQLAlchemy Model Development

#### Base Model Pattern
```python
from sqlalchemy import Column, Integer, DateTime, String, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### Domain-Specific Models
```python
class DomainCheck(Base):
    __tablename__ = "domain_checks"
    
    # Primary fields
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    domain = Column(String, nullable=False, index=True)
    
    # DNS record fields (store as JSON)
    mx_record = Column(Text)  # JSON string
    spf_record = Column(Text)  # JSON string
    dkim_record = Column(Text)  # JSON string
    dmarc_record = Column(Text)  # JSON string
    
    # Analysis results
    score = Column(Integer, nullable=False)
    grade = Column(String(5), nullable=False)
    issues = Column(Text)  # JSON array of issues
    recommendations = Column(Text)  # JSON array of recommendations
    security_summary = Column(Text)  # JSON object
    
    # Metadata
    opt_in_marketing = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_domain_email', 'domain', 'email'),
        Index('idx_created_at', 'created_at'),
    )
```

### Alembic Migration Patterns

#### Creating Migrations
```bash
# Generate migration for model changes
alembic revision --autogenerate -m "Add security_summary column to domain_checks"

# Manual migration for complex changes
alembic revision -m "Add indexes for performance optimization"
```

#### Migration Script Template
```python
"""Add security_summary column to domain_checks

Revision ID: abc123
Revises: def456
Create Date: 2025-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123'
down_revision = 'def456'
branch_labels = None
depends_on = None

def upgrade():
    # Add new column
    op.add_column('domain_checks', 
                  sa.Column('security_summary', sa.Text(), nullable=True))
    
    # Add index if needed
    op.create_index('idx_security_summary', 'domain_checks', ['security_summary'])

def downgrade():
    # Remove index first
    op.drop_index('idx_security_summary', 'domain_checks')
    
    # Remove column
    op.drop_column('domain_checks', 'security_summary')
```

### Database Session Management

#### Session Dependency
```python
from sqlalchemy.orm import Session
from database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### Transaction Handling
```python
def create_domain_check_with_usage(db: Session, check_data: dict, usage_data: dict):
    """Create domain check and update usage in a single transaction."""
    try:
        # Create domain check
        domain_check = DomainCheck(**check_data)
        db.add(domain_check)
        
        # Update or create usage record
        usage = db.query(DomainUsage).filter_by(**usage_filter).first()
        if usage:
            usage.check_count += 1
            usage.last_check = datetime.utcnow()
        else:
            usage = DomainUsage(**usage_data)
            db.add(usage)
        
        # Commit all changes
        db.commit()
        db.refresh(domain_check)
        return domain_check
        
    except Exception as e:
        db.rollback()
        logger.error(f"Transaction failed: {e}")
        raise
```

## Email Service Development

### Jinja2 Template System

#### Email Service Class Structure
```python
from jinja2 import Environment, FileSystemLoader
import os

class EmailService:
    def __init__(self):
        # Setup Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
        
    def _prepare_template_data(self, **kwargs) -> dict:
        """Prepare common template data."""
        base_data = {
            'company_name': 'Raposa',
            'current_year': datetime.now().year,
            'support_email': 'support@raposa.tech',
            'website_url': 'https://raposa.tech'
        }
        base_data.update(kwargs)
        return base_data
```

#### Template Rendering Pattern
```python
async def send_domain_report(self, to_email: str, domain: str, analysis_results: dict, **kwargs):
    """Send comprehensive domain analysis report."""
    try:
        # Prepare template data
        template_data = self._prepare_template_data(
            domain=domain,
            analysis_results=analysis_results,
            recipient_email=to_email,
            **kwargs
        )
        
        # Render HTML template
        html_template = self.jinja_env.get_template('domain_report.html')
        html_content = html_template.render(**template_data)
        
        # Render text template
        text_template = self.jinja_env.get_template('domain_report.txt')
        text_content = text_template.render(**template_data)
        
        # Send email
        return await self._send_email(
            to_email=to_email,
            subject=f"Domain Security Report for {domain}",
            html_content=html_content,
            text_content=text_content
        )
        
    except Exception as e:
        logger.error(f"Failed to send domain report to {to_email}: {e}")
        return False
```

### Email Template Development

#### HTML Template Structure
```html
<!-- templates/domain_report.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Domain Security Report - {{ domain }}</title>
    <style>
        /* Brand-compliant styles */
        .container { max-width: 600px; margin: 0 auto; }
        .header { background: #1a1a1a; color: white; padding: 20px; }
        .content { padding: 20px; }
        .score { font-size: 24px; font-weight: bold; }
        .grade-A { color: #28a745; }
        .grade-B { color: #ffc107; }
        .grade-C { color: #fd7e14; }
        .grade-F { color: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ company_name }} Domain Security Report</h1>
            <p>Comprehensive analysis for {{ domain }}</p>
        </div>
        
        <div class="content">
            <div class="score-section">
                <h2>Security Score</h2>
                <div class="score grade-{{ analysis_results.grade.split('+')[0] }}">
                    {{ analysis_results.score }}/100 (Grade: {{ analysis_results.grade }})
                </div>
            </div>
            
            {% if analysis_results.issues %}
            <div class="issues-section">
                <h3>Security Issues Found</h3>
                <ul>
                {% for issue in analysis_results.issues %}
                    <li>{{ issue }}</li>
                {% endfor %}
                </ul>
            </div>
            {% endif %}
            
            {% if analysis_results.recommendations %}
            <div class="recommendations-section">
                <h3>Recommendations</h3>
                <ul>
                {% for recommendation in analysis_results.recommendations %}
                    <li>{{ recommendation }}</li>
                {% endfor %}
                </ul>
            </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>&copy; {{ current_year }} {{ company_name }}. All rights reserved.</p>
            <p>Questions? Contact us at {{ support_email }}</p>
        </div>
    </div>
</body>
</html>
```

#### Text Template Structure
```text
# templates/domain_report.txt
{{ company_name }} Domain Security Report
=======================================

Domain: {{ domain }}
Analysis Date: {{ analysis_results.created_at }}

SECURITY SCORE
--------------
Score: {{ analysis_results.score }}/100
Grade: {{ analysis_results.grade }}

{% if analysis_results.issues %}
SECURITY ISSUES FOUND
--------------------
{% for issue in analysis_results.issues %}
• {{ issue }}
{% endfor %}
{% endif %}

{% if analysis_results.recommendations %}
RECOMMENDATIONS
--------------
{% for recommendation in analysis_results.recommendations %}
• {{ recommendation }}
{% endfor %}
{% endif %}

DNS RECORDS SUMMARY
------------------
MX Record: {{ "✓ Configured" if analysis_results.mx_record else "✗ Not found" }}
SPF Record: {{ "✓ Configured" if analysis_results.spf_record else "✗ Not found" }}
DKIM Record: {{ "✓ Configured" if analysis_results.dkim_record else "✗ Not found" }}
DMARC Record: {{ "✓ Configured" if analysis_results.dmarc_record else "✗ Not found" }}

---
© {{ current_year }} {{ company_name }}. All rights reserved.
Questions? Contact us at {{ support_email }}
Visit us at {{ website_url }}
```

### SendGrid Integration Pattern

#### Email Sending Implementation
```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content

async def _send_email(self, to_email: str, subject: str, html_content: str, text_content: str):
    """Send email using SendGrid."""
    try:
        # Create mail object
        mail = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject
        )
        
        # Add content
        mail.add_content(Content("text/plain", text_content))
        mail.add_content(Content("text/html", html_content))
        
        # Send email
        response = self.sg_client.send(mail)
        
        if response.status_code in [200, 201, 202]:
            logger.info(f"Email sent successfully to {to_email}")
            return True
        else:
            logger.error(f"SendGrid API error: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        return False
```

### Background Task Integration

#### Email Task Pattern
```python
async def send_domain_report_email(email: str, domain: str, analysis_results: dict):
    """Background task for sending domain reports."""
    try:
        email_service = get_email_service()
        
        # Check if first-time user
        is_first_check = await check_if_first_time_user(email)
        
        if is_first_check:
            # Send welcome email
            await email_service.send_welcome_email(email, domain)
        
        # Send domain report
        success = await email_service.send_domain_report(
            to_email=email,
            domain=domain,
            analysis_results=analysis_results
        )
        
        # Log result
        if success:
            logger.info(f"Domain report sent successfully to {email}")
        else:
            logger.error(f"Failed to send domain report to {email}")
            
    except Exception as e:
        logger.error(f"Background email task failed: {e}")
```

Remember to test email templates thoroughly and follow brand guidelines for all email communications.
