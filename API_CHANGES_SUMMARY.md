# Quick Reference: Optional Email API Changes

## 🔄 What Changed

### Request Schema
```diff
{
- "email": "required@email.com",     // WAS: Required
+ "email": "optional@email.com",     // NOW: Optional (can be null/omitted)
  "domain": "example.com",           // Still required
  "opt_in_marketing": false          // Still optional
}
```

### Response Schema
```diff
{
  "id": 123,
- "email": "user@example.com",       // WAS: Always string
+ "email": null,                     // NOW: Can be null for anonymous users
  "domain": "example.com",
  // ... rest unchanged
}
```

## 🚦 Rate Limiting Rules

| User Type | Limit | Tracking Method | Upgrade Message |
|-----------|-------|----------------|-----------------|
| **Anonymous** | 1 check/domain/month | Domain-based | "Provide an email address for additional checks!" |
| **Registered** | 15 checks/domain/month | Email + Domain | "Maximum 15 checks per domain per month. Create an account for more checks!" |

## 📝 Frontend Checklist

- [ ] Make email field optional in forms
- [ ] Handle `email: null` in responses
- [ ] Show conversion prompts for anonymous users
- [ ] Handle new rate limit messages
- [ ] Track conversion events (anonymous → email)
- [ ] Test both anonymous and registered flows

## 🎯 UX Goals

1. **Zero friction** for first-time users
2. **Progressive enhancement** - show value first, ask for email second
3. **Clear conversion path** when limits are reached
4. **Natural upgrade messaging** to encourage email signup

## 🔧 Quick Test Commands

```bash
# Anonymous check (first time)
curl -X POST "/check-domain" -d '{"domain": "test.com"}'

# Anonymous check (rate limited)
curl -X POST "/check-domain" -d '{"domain": "test.com"}'

# Registered check
curl -X POST "/check-domain" -d '{"domain": "test.com", "email": "user@example.com"}'
```

## 🎨 Conversion Messages

Use these messages to guide users:

- **After successful anonymous check**: "Want more checks? Enter email for 15 per month"
- **When anonymous limit hit**: "Add your email to continue checking domains"
- **When registered limit hit**: "Upgrade your account for unlimited checks"
