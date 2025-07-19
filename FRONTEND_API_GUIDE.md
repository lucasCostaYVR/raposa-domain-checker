# API Documentation: Optional Email & Progressive Rate Limiting

## Overview

The domain check API now supports **progressive enhancement** with optional email collection:

- **Anonymous users**: 1 free check per domain per month (domain-based tracking)
- **Registered users**: 15 checks per domain per month (email required)
- **Natural conversion**: Users see value before being asked for email

## API Endpoint

```
POST /check-domain
```

## Request Schema Changes

### Before (Required Email)
```json
{
  "email": "user@example.com",     // REQUIRED
  "domain": "example.com",         // required
  "opt_in_marketing": false        // optional, default false
}
```

### After (Optional Email)
```json
{
  "email": "user@example.com",     // OPTIONAL - can be null or omitted
  "domain": "example.com",         // required
  "opt_in_marketing": false        // optional, default false
}
```

## Response Schema Changes

### Response Structure
```json
{
  "id": 123,
  "email": null,                   // NOW NULLABLE - can be null for anonymous users
  "domain": "example.com",
  "mx_record": { /* ... */ },
  "spf_record": { /* ... */ },
  "dkim_record": { /* ... */ },
  "dmarc_record": { /* ... */ },
  "score": 85,
  "grade": "A",
  "issues": ["..."],
  "recommendations": ["..."],
  "security_summary": { /* ... */ },
  "created_at": "2025-07-19T03:28:59.368649Z",
  "opt_in_marketing": false
}
```

## Rate Limiting Behavior

### Success Cases

#### 1. Anonymous User - First Check (✅ Success)
**Request:**
```bash
curl -X POST "https://api.domainchecker.raposa.tech/check-domain" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "github.com"
  }'
```

**Response:** `200 OK`
```json
{
  "id": 123,
  "email": null,
  "domain": "github.com",
  "score": 85,
  "grade": "A",
  // ... full analysis results
}
```

#### 2. Registered User - Multiple Checks (✅ Success)
**Request:**
```bash
curl -X POST "https://api.domainchecker.raposa.tech/check-domain" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "github.com",
    "email": "user@example.com"
  }'
```

**Response:** `200 OK`
```json
{
  "id": 124,
  "email": "user@example.com",
  "domain": "github.com",
  "score": 85,
  "grade": "A",
  // ... full analysis results + email will be sent
}
```

### Rate Limit Cases

#### 3. Anonymous User - Second Check (❌ Rate Limited)
**Request:**
```bash
curl -X POST "https://api.domainchecker.raposa.tech/check-domain" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "github.com"
  }'
```

**Response:** `429 Too Many Requests`
```json
{
  "detail": "You've already checked this domain this month. Provide an email address for additional checks!"
}
```

#### 4. Registered User - Exceeded Monthly Limit (❌ Rate Limited)
**Request:**
```bash
curl -X POST "https://api.domainchecker.raposa.tech/check-domain" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "email": "user@example.com"
  }'
```

**Response:** `429 Too Many Requests`
```json
{
  "detail": "Domain check limit exceeded. Maximum 15 checks per domain per month. Create an account for more checks!"
}
```

## Frontend Implementation Guide

### 1. Form Design Changes

#### Before: Required Email Form
```html
<form>
  <input type="text" name="domain" placeholder="Enter domain" required />
  <input type="email" name="email" placeholder="Your email" required />
  <button type="submit">Check Domain Security</button>
</form>
```

#### After: Progressive Enhancement Form
```html
<form>
  <input type="text" name="domain" placeholder="Enter domain" required />

  <!-- Email section - initially hidden or optional -->
  <div id="email-section" class="optional">
    <input type="email" name="email" placeholder="Email (optional for more checks)" />
    <small>Get results via email and unlock 15 checks per domain per month</small>
  </div>

  <button type="submit">Check Domain Security</button>
</form>
```

### 2. JavaScript Implementation

```javascript
class DomainChecker {
  async checkDomain(domain, email = null) {
    const payload = { domain };
    if (email) {
      payload.email = email;
      payload.opt_in_marketing = false; // or get from checkbox
    }

    try {
      const response = await fetch('/check-domain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const result = await response.json();
        this.handleSuccess(result);
        return result;
      } else if (response.status === 429) {
        const error = await response.json();
        this.handleRateLimit(error.detail);
      } else {
        this.handleError('Analysis failed');
      }
    } catch (error) {
      this.handleError('Network error');
    }
  }

  handleSuccess(result) {
    // Display domain analysis results
    this.displayResults(result);

    // Show conversion prompt if anonymous user
    if (!result.email) {
      this.showEmailPrompt();
    }
  }

  handleRateLimit(message) {
    if (message.includes("Provide an email address")) {
      // Anonymous user hit limit - show email form
      this.showEmailRequiredPrompt();
    } else {
      // Registered user hit limit - show upgrade prompt
      this.showUpgradePrompt();
    }
  }

  showEmailRequiredPrompt() {
    // Show modal or inline message
    this.showMessage({
      type: 'info',
      title: 'Want more checks?',
      message: 'Enter your email to get 15 checks per domain per month',
      action: 'Show email form'
    });
  }

  showEmailPrompt() {
    // Conversion prompt for successful anonymous users
    this.showMessage({
      type: 'success',
      title: 'Great results!',
      message: 'Want to check more domains? Enter your email for 15 checks per month',
      action: 'Get more checks'
    });
  }
}
```

### 3. UX Flow Recommendations

#### Step 1: Initial Experience (No Email Required)
```
[Domain Input: ________________] [Check Security →]
                    ↓
              Analysis Results
                    ↓
    "Want more checks? Enter email for 15 per month"
```

#### Step 2: Rate Limited (Email Required)
```
[Domain Input: ________________] [Check Security →]
                    ↓
    "You've checked this domain. Add email for more!"
                    ↓
[Email Input: __________________] [Get More Checks →]
```

### 4. Error Handling

```javascript
const ERROR_MESSAGES = {
  ANONYMOUS_LIMIT: 'You\'ve already checked this domain this month. Provide an email address for additional checks!',
  REGISTERED_LIMIT: 'Domain check limit exceeded. Maximum 15 checks per domain per month. Create an account for more checks!',
  INVALID_DOMAIN: 'Invalid or unsafe domain format',
  NETWORK_ERROR: 'Network error occurred. Please try again.',
  SERVER_ERROR: 'Analysis failed. Please try again later.'
};

function handleApiError(response, errorData) {
  switch (response.status) {
    case 422:
      return ERROR_MESSAGES.INVALID_DOMAIN;
    case 429:
      return errorData.detail; // Use specific rate limit message
    case 500:
      return ERROR_MESSAGES.SERVER_ERROR;
    default:
      return ERROR_MESSAGES.NETWORK_ERROR;
  }
}
```

### 5. Conversion Optimization

```javascript
// Track conversion events
function trackConversion(event, data) {
  // Analytics tracking
  if (typeof gtag !== 'undefined') {
    gtag('event', event, {
      'event_category': 'Domain Checker',
      'event_label': data.domain,
      'value': data.score
    });
  }
}

// Usage examples
trackConversion('anonymous_check_success', { domain: 'example.com', score: 85 });
trackConversion('email_provided', { domain: 'example.com', email: 'user@example.com' });
trackConversion('rate_limit_hit', { domain: 'example.com', type: 'anonymous' });
```

## Testing Examples

### Test Anonymous Flow
```bash
# First check - should succeed
curl -X POST "http://localhost:8000/check-domain" \
  -H "Content-Type: application/json" \
  -d '{"domain": "testdomain1.com"}'

# Second check same domain - should be rate limited
curl -X POST "http://localhost:8000/check-domain" \
  -H "Content-Type: application/json" \
  -d '{"domain": "testdomain1.com"}'
```

### Test Registered User Flow
```bash
# With email - should succeed even after anonymous limit
curl -X POST "http://localhost:8000/check-domain" \
  -H "Content-Type: application/json" \
  -d '{"domain": "testdomain1.com", "email": "test@example.com"}'
```

## Migration Notes

### Database Changes
- `domain_checks.email` is now nullable
- Removed `anonymous_usage` table (IP-based tracking eliminated)
- Removed `client_ip` column from `domain_checks` table
- Uses domain-based rate limiting only via `domain_usage` table

### Backward Compatibility
- ✅ Existing API calls with email still work exactly the same
- ✅ Response format unchanged (email field just nullable now)
- ✅ All existing rate limiting for registered users preserved

## Analytics & Monitoring

Track these metrics to measure success:

1. **Conversion Rate**: Anonymous users → Email provided
2. **Engagement**: Anonymous vs registered user domain checks
3. **Rate Limit Events**: How often users hit limits
4. **Funnel Analysis**: Domain check → Email → Subsequent checks

This implementation should significantly improve your conversion rates by removing the initial email barrier while maintaining a clear path to registration!
