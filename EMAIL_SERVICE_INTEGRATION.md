# Email Service Redis Queue Integration Guide

## Overview
The Raposa Domain Checker adds domain report email messages to a Redis queue for processing by a separate email service. This document describes the integration format and message structure required by the email service.

**Important Notes**:
- **Welcome emails** are handled by a separate identity service, not this email service
- **Anonymous domain checks** (without email) do not trigger any email messages
- Only domain checks with a provided email address will generate Redis queue messages

## 🎯 Redis Queue Configuration

### Connection Details
- **Redis URL**: Use environment variable `REDIS_URL`
- **Queue Name**: `raposa_email_queue`
- **Redis Method**: `ZADD` (sorted set with priority scoring)
- **Message Format**: JSON strings added to Redis sorted set with priority scores

### Example Queue Consumer (Python)
```python
import redis
import json

redis_client = redis.from_url(os.getenv("REDIS_URL"))

# Process messages from sorted set queue (highest priority first)
while True:
    # ZPOPMAX gets highest priority message
    result = redis_client.zpopmax("raposa_email_queue", 1)
    if result:
        message_data, score = result[0]
        email_data = json.loads(message_data)
        process_email_message(email_data)
```

## 📝 Required Message Format

### Message Structure
All messages are JSON objects with this exact format expected by the email service:

```json
{
  "to_email": "user@example.com",
  "template": "domain_report",
  "data": {
    "domain": "example.com",
    "score": 70,
    "grade": "B",
    "security_level": "Good",
    "analysis_results": { /* Complete domain analysis object */ },
    "report_date": "July 22, 2025",
    "company_name": "Raposa"
  },
  "priority": "medium",
  "event_type": "domain_report.requested"
}
```

### Domain Report Message
When a user requests a domain analysis **with an email address**, this message is added to the queue containing **the complete analysis results**:

**Note**: Anonymous domain checks (without email) do not trigger email messages.

```json
{
  "to_email": "lucas.costa.1194@gmail.com",
  "template": "domain_report",
  "data": {
    "domain": "example.com",
    "score": 70,
    "grade": "B",
    "security_level": "Good",
    "analysis_results": {
      "id": 140,
      "domain": "example.com",
      "mx_record": {
        "records": [{"preference": 1, "exchange": "smtp.google.com"}],
        "status": "valid",
        "issues": [],
        "score": 20,
        "explanation": {
          "what_is": "MX (Mail Exchange) records tell other email servers...",
          "current_status": "✅ Your domain is properly configured...",
          "risk_if_misconfigured": ""
        }
      },
      "spf_record": {
        "record": "v=spf1 include:spf.brevo.com include:sendgrid.net ~all",
        "status": "valid",
        "mechanisms": ["include:spf.brevo.com", "include:sendgrid.net", "~all"],
        "issues": [],
        "score": 20,
        "explanation": { /* ... */ }
      },
      "dkim_record": {
        "selectors": {},
        "status": "missing",
        "issues": ["No DKIM records found - emails may be marked as spam"],
        "score": 0,
        "explanation": { /* ... */ }
      },
      "dmarc_record": {
        "record": "v=DMARC1; p=reject; rua=mailto:rua@dmarc.brevo.com",
        "status": "valid",
        "policy": {"v": "DMARC1", "p": "reject", "rua": "mailto:rua@dmarc.brevo.com"},
        "issues": [],
        "score": 30,
        "explanation": { /* ... */ }
      },
      "score": 70,
      "grade": "B",
      "issues": ["No DKIM records found - emails may be marked as spam"],
      "recommendations": ["Set up DKIM signing to improve email authentication"],
      "security_summary": {
        "security_level": "Good",
        "overall_message": "Your domain has decent email security...",
        "components_configured": "3/4 email security components properly configured",
        "grade_meaning": "Decent email security with several areas that should be improved.",
        "priority_actions": ["Configure DKIM for email authentication"],
        "protection_status": {
          "spoofing_protection": "Protected",
          "email_delivery": "Working",
          "authentication": "Weak"
        }
      },
      "created_at": "2025-07-23T00:31:05.544773Z",
      "opt_in_marketing": false
    },
    "report_date": "July 22, 2025",
    "company_name": "Raposa"
  },
  "priority": "medium",
  "event_type": "domain_report.requested"
}
```

**Key Points**:
- The `analysis_results` object contains the **complete domain analysis** including all DNS records, scores, grades, issues, and recommendations
- The message is wrapped in the email service's expected format with `template`, `data`, and `priority` fields
- Additional fields like `score`, `grade`, and `security_level` are extracted for easy template access
- The `report_date` is formatted as a human-readable date string
- All necessary data for email templating is included in this single message
- **Anonymous domain checks do not trigger email messages** - only requests with email addresses generate queue messages

## Email Templates Required

### Domain Report Email
**Subject**: `Domain Security Analysis Report for {domain}`

**Required Template Variables**:
- `domain`: The analyzed domain name
- `score`: Overall security score (0-100)
- `grade`: Letter grade (F, D, C-, C, C+, B-, B, B+, A-, A, A+)
- `security_level`: Text description (Poor, Fair, Good, Excellent)
- `mx_record`: MX record analysis object
- `spf_record`: SPF record analysis object  
- `dkim_record`: DKIM record analysis object
- `dmarc_record`: DMARC record analysis object
- `issues`: Array of security issues found
- `recommendations`: Array of improvement recommendations
- `security_summary`: Summary object with overall assessment

**Template should include**:
- Professional header with Raposa branding
- Domain name and overall score/grade prominently displayed
- Breakdown of each DNS record type (MX, SPF, DKIM, DMARC)
- Status indicators (✅ good, ⚠️ warning, ❌ critical)
- Clear explanations for each component
- Action items and recommendations
- Footer with company information

**Note**: Welcome emails are handled by the separate identity service, not this email service.

## 🔧 Backend Publisher Implementation

The domain checker backend uses this code to publish messages to the email service queue:

```python
import redis
import json
from datetime import datetime
import os

def send_domain_report_email(to_email: str, domain: str, analysis_results: dict):
    """Send domain report via email service queue"""
    
    redis_client = redis.from_url(os.getenv("REDIS_URL"))
    
    # Format message for email service
    email_message = {
        "to_email": to_email,
        "template": "domain_report",
        "data": {
            "domain": domain,
            "score": analysis_results.get("score", 0),
            "grade": analysis_results.get("grade", "F"),
            "security_level": analysis_results.get("security_summary", {}).get("security_level", "Poor"),
            "analysis_results": analysis_results,
            "report_date": datetime.utcnow().strftime("%B %d, %Y"),
            "company_name": "Raposa"
        },
        "priority": "medium",
        "event_type": "domain_report.requested"
    }
    
    # Add to email queue (ZADD creates sorted set with priority scoring)
    priority_score = {"high": 1000, "medium": 500, "low": 100}.get("medium", 500)
    timestamp_score = datetime.utcnow().timestamp() / 1000000
    final_score = priority_score + timestamp_score
    
    redis_client.zadd("raposa_email_queue", {json.dumps(email_message): final_score})
    print(f"📧 Domain report email queued for {to_email} (domain: {domain}) with score {final_score}")
```

### Key Changes from Previous Implementation

1. **Queue Name**: `raposa_email_queue` (sorted set)
2. **Redis Method**: `ZADD` (not LPUSH) - creates sorted set with priority scoring
3. **Priority Scoring**: High=1000, Medium=500, Low=100 + timestamp for ordering
4. **Message Structure**: Email service compatible format with `template`, `data`, `priority`, `event_type`
5. **Template Name**: `domain_report` template identifier


## Processing Logic

### Message Consumer Implementation

```python
def process_email_message(message_data):
    """Process email message from Redis queue"""
    
    try:
        email_data = json.loads(message_data)
        template = email_data.get('template')
        
        if template == 'domain_report':
            send_domain_report_email(
                to_email=email_data['to_email'],
                template_data=email_data['data']
            )
        else:
            logger.warning(f"Unknown template: {template}")
            
    except Exception as e:
        logger.error(f"Failed to process email message: {e}")
        # Implement retry logic or dead letter queue
```

### Error Handling Requirements

1. **Invalid JSON**: Log error and skip message
2. **Missing required fields**: Log error with message details
3. **SendGrid API failures**: Implement exponential backoff retry
4. **Template rendering errors**: Log error and send fallback email
5. **Rate limiting**: Implement queue processing throttling

### Monitoring and Logging

Log the following events:
- Message received from Redis
- Email sent successfully
- SendGrid API errors
- Template rendering errors
- Processing time metrics

## SendGrid Configuration

### Required Environment Variables
```bash
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=noreply@raposa.tech
SENDGRID_FROM_NAME=Raposa Domain Checker
```

### Email Templates
Create SendGrid dynamic template for:
1. **Domain Report**: Professional template with analysis breakdown

## Testing

### Test Message Publisher
Use this script to test the email service with the correct message format:

```python
import redis
import json
from datetime import datetime

def publish_test_message():
    redis_client = redis.from_url("your_redis_url")
    
    test_message = {
        "to_email": "test@example.com",
        "template": "domain_report",
        "data": {
            "domain": "test.com",
            "score": 85,
            "grade": "A",
            "security_level": "Excellent",
            "analysis_results": {
                "score": 85,
                "grade": "A",
                "mx_record": {"status": "valid", "score": 20},
                "spf_record": {"status": "valid", "score": 25},
                "dkim_record": {"status": "valid", "score": 20},
                "dmarc_record": {"status": "valid", "score": 20},
                "issues": [],
                "recommendations": ["Great job! Your email security is well configured."],
                "security_summary": {
                    "security_level": "Excellent",
                    "overall_message": "Your domain has excellent email security.",
                    "components_configured": "4/4 email security components properly configured"
                }
            },
            "report_date": datetime.utcnow().strftime("%B %d, %Y"),
            "company_name": "Raposa"
        },
        "priority": "medium",
        "event_type": "domain_report.requested"
    }
    
    # Add to sorted set with priority scoring
    priority_score = {"high": 1000, "medium": 500, "low": 100}.get("medium", 500)
    timestamp_score = datetime.utcnow().timestamp() / 1000000
    final_score = priority_score + timestamp_score
    
    redis_client.zadd("raposa_email_queue", {json.dumps(test_message): final_score})
    print("Test message queued")
```

### Validation Checklist
- [ ] Redis connection established
- [ ] Processing messages from `raposa_email_queue` sorted set
- [ ] Using `ZPOPMAX` or `ZPOPMIN` to get messages from sorted set
- [ ] JSON parsing working correctly
- [ ] Domain report emails sending with `domain_report` template
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] SendGrid template created
- [ ] Rate limiting implemented

## Expected Message Volume

- **Development**: 1-10 messages per day
- **Production**: 100-1000 messages per day initially
- **Peak**: Up to 10,000 messages per day (plan for scaling)

## Architecture Notes

- Messages are added to Redis sorted set via ZADD (persistent queue with priority)
- Messages persist in sorted set until consumed by email service
- Use ZPOPMAX to consume highest priority messages first
- Priority scoring: High=1000, Medium=500, Low=100 + timestamp
- Process messages idempotently (same message twice should be safe)
- Queue name: `raposa_email_queue`
- Message format: Email service compatible structure

## Contact

For questions about the message format or integration:
- Domain Checker API: https://api.domainchecker.raposa.tech
- Development Environment: https://stage.domainchecker.raposa.tech
- Debug endpoint: `/debug/redis-queue` (shows connection status)
