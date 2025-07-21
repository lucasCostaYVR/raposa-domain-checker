# 🔐 **Raposa Identity Service - Integration Guide**

## **Overview**
The Raposa Identity Service is the central authentication and authorization provider for all Raposa ecosystem services. It provides JWT-based authentication, user management, and OAuth2/OIDC capabilities.

### **Base URLs**
- **Production**: `https://raposa-identity-production.up.railway.app`
- **Development**: `http://localhost:8000`

### **Health Check**
- **Endpoint**: `GET /health/`
- **Response**: `{"status": "healthy", "timestamp": "2025-07-21T03:00:00.000000"}`

---

## **🔑 Authentication Flow**

### **1. User Registration**
Register new users in your service by redirecting to the Identity Service or using the API directly.

**Endpoint**: `POST /auth/register`

```bash
curl -X POST "https://raposa-identity-production.up.railway.app/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe",
    "company": "Example Corp"
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe",
    "company": "Example Corp",
    "is_active": true,
    "email_verified": false,
    "created_at": "2025-07-21T03:00:00.000000"
  }
}
```

### **2. User Login**
Authenticate existing users and obtain JWT tokens.

**Endpoint**: `POST /auth/login`

```bash
curl -X POST "https://raposa-identity-production.up.railway.app/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

**Response**: Same as registration response.

### **3. Token Refresh**
Refresh access tokens using refresh tokens.

**Endpoint**: `POST /auth/refresh`

```bash
curl -X POST "https://raposa-identity-production.up.railway.app/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## **👤 User Management Endpoints**

### **Get Current User Profile**
**Endpoint**: `GET /users/me`
**Authentication**: Required (Bearer token)

```bash
curl -X GET "https://raposa-identity-production.up.railway.app/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "first_name": "John",
  "last_name": "Doe",
  "company": "Example Corp",
  "is_active": true,
  "email_verified": true,
  "created_at": "2025-07-21T03:00:00.000000"
}
```

### **Update User Profile**
**Endpoint**: `PUT /users/me`
**Authentication**: Required (Bearer token)

```bash
curl -X PUT "https://raposa-identity-production.up.railway.app/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "company": "New Company Inc"
  }'
```

### **Change Password**
**Endpoint**: `POST /users/change-password`
**Authentication**: Required (Bearer token)

```bash
curl -X POST "https://raposa-identity-production.up.railway.app/users/change-password" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "CurrentPassword123!",
    "new_password": "NewSecurePassword456!"
  }'
```

---

## **🔄 Password Reset Flow**

### **1. Request Password Reset**
**Endpoint**: `POST /auth/request-password-reset`

```bash
curl -X POST "https://raposa-identity-production.up.railway.app/auth/request-password-reset" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

**Response**:
```json
{
  "message": "If the email exists, a password reset link has been sent"
}
```

### **2. Reset Password with Token**
**Endpoint**: `POST /auth/reset-password`

```bash
curl -X POST "https://raposa-identity-production.up.railway.app/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123def456ghi789",
    "new_password": "NewSecurePassword789!"
  }'
```

---

## **✉️ Email Verification**

### **Verify Email**
**Endpoint**: `POST /auth/verify-email`

```bash
curl -X POST "https://raposa-identity-production.up.railway.app/auth/verify-email" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "verification_token_here"
  }'
```

### **Resend Verification Email**
**Endpoint**: `POST /auth/resend-verification`
**Authentication**: Required (Bearer token)

```bash
curl -X POST "https://raposa-identity-production.up.railway.app/auth/resend-verification" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## **🔐 JWT Token Information**

### **Token Structure**
- **Access Token**: 30 minutes expiration
- **Refresh Token**: 7 days expiration
- **Algorithm**: HS256
- **Header**: `Authorization: Bearer {access_token}`

### **JWT Payload Example**
```json
{
  "sub": "1",
  "email": "user@example.com",
  "username": "username",
  "exp": 1642781234,
  "iat": 1642779434,
  "type": "access"
}
```

### **Token Validation**
Your service should validate JWT tokens by:
1. Verifying the signature with the shared secret
2. Checking expiration (`exp` claim)
3. Extracting user information from payload

---

## **🛠️ Integration Patterns**

### **Pattern 1: Direct API Integration**
Use the Identity Service API directly from your service backend.

```python
import requests
import jwt
from datetime import datetime

class IdentityServiceClient:
    def __init__(self, base_url, jwt_secret):
        self.base_url = base_url
        self.jwt_secret = jwt_secret
    
    def validate_token(self, token):
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user_info(self, token):
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{self.base_url}/users/me", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None

# Usage
identity_client = IdentityServiceClient(
    "https://raposa-identity-production.up.railway.app",
    "your-jwt-secret"
)

# Validate token
user_data = identity_client.validate_token(access_token)
if user_data:
    print(f"User {user_data['email']} is authenticated")
```

### **Pattern 2: Middleware Integration**
Create middleware in your service to handle authentication.

```python
# FastAPI Example
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    user_data = identity_client.validate_token(token.credentials)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_data

# Use in your endpoints
@app.get("/protected-endpoint")
async def protected_endpoint(user = Depends(get_current_user)):
    return {"message": f"Hello {user['email']}"}
```

### **Pattern 3: Redirect-based Authentication**
Redirect users to the Identity Service for authentication.

```javascript
// Frontend JavaScript
function redirectToLogin() {
    const returnUrl = encodeURIComponent(window.location.href);
    window.location.href = `https://raposa-identity-production.up.railway.app/login?return_url=${returnUrl}`;
}

// Handle return from Identity Service
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');
if (token) {
    localStorage.setItem('access_token', token);
    // Remove token from URL
    window.history.replaceState({}, document.title, window.location.pathname);
}
```

---

## **📡 Event Integration (Redis)**

### **Subscribe to User Events**
The Identity Service publishes events to Redis that your service can subscribe to.

```python
import redis
import json

redis_client = redis.from_url("redis://default:NrdOAHDxlfSxvrvEJuRxmZPTZEKxBQym@yamanote.proxy.rlwy.net:58674")
pubsub = redis_client.pubsub()

# Subscribe to all identity events
pubsub.subscribe("domain_events")

async def handle_identity_events():
    for message in pubsub.listen():
        if message['type'] == 'message':
            event_data = json.loads(message['data'])
            
            if event_data['service'] == 'raposa-identity':
                await process_identity_event(event_data)

async def process_identity_event(event_data):
    event_type = event_data['event_type']
    user_data = event_data['event_data']
    
    if event_type == 'identity.user.registered':
        # Handle new user registration
        await create_user_profile_in_service(user_data)
    elif event_type == 'identity.user.profile_updated':
        # Handle profile updates
        await update_user_profile_in_service(user_data)
    # ... handle other events
```

### **Available Events**
See `REDIS_EVENT_MESSAGES.md` for complete event documentation:
- `identity.user.registered`
- `identity.user.login_success`
- `identity.user.login_failed`
- `identity.password.reset_requested`
- `identity.password.changed`
- `identity.user.email_verified`
- `identity.user.profile_updated`
- `identity.user.deactivated`

---

## **🚀 Quick Start Integration**

### **1. Environment Variables**
Add these to your service's environment:

```bash
# Identity Service Configuration
IDENTITY_SERVICE_URL=https://raposa-identity-production.up.railway.app
JWT_SECRET_KEY=your-shared-jwt-secret
REDIS_URL=redis://default:NrdOAHDxlfSxvrvEJuRxmZPTZEKxBQym@yamanote.proxy.rlwy.net:58674

# For local development
IDENTITY_SERVICE_URL=http://localhost:8000
```

### **2. Basic Integration Test**
Test your integration with this simple flow:

```python
import requests

# Test 1: Health check
response = requests.get("https://raposa-identity-production.up.railway.app/health/")
print(f"Health check: {response.json()}")

# Test 2: Register a test user
register_data = {
    "email": "test@yourservice.com",
    "password": "TestPassword123!",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User"
}

response = requests.post(
    "https://raposa-identity-production.up.railway.app/auth/register",
    json=register_data
)

if response.status_code == 200:
    auth_data = response.json()
    access_token = auth_data['access_token']
    print(f"Registration successful! Token: {access_token[:20]}...")
    
    # Test 3: Get user profile
    headers = {"Authorization": f"Bearer {access_token}"}
    profile_response = requests.get(
        "https://raposa-identity-production.up.railway.app/users/me",
        headers=headers
    )
    print(f"User profile: {profile_response.json()}")
else:
    print(f"Registration failed: {response.json()}")
```

### **3. Frontend Integration**
Add authentication to your frontend:

```javascript
// Store token
function storeAuthToken(token) {
    localStorage.setItem('raposa_access_token', token);
}

// Get stored token
function getAuthToken() {
    return localStorage.getItem('raposa_access_token');
}

// Add token to API requests
function makeAuthenticatedRequest(url, options = {}) {
    const token = getAuthToken();
    if (token) {
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };
    }
    return fetch(url, options);
}

// Check if user is authenticated
async function isAuthenticated() {
    const token = getAuthToken();
    if (!token) return false;
    
    try {
        const response = await makeAuthenticatedRequest(
            'https://raposa-identity-production.up.railway.app/users/me'
        );
        return response.ok;
    } catch {
        return false;
    }
}

// Login flow
async function login(email, password) {
    const response = await fetch('https://raposa-identity-production.up.railway.app/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    
    if (response.ok) {
        const data = await response.json();
        storeAuthToken(data.access_token);
        return data;
    }
    throw new Error('Login failed');
}

// Logout
function logout() {
    localStorage.removeItem('raposa_access_token');
    // Optionally redirect to login page
}
```

---

## **⚠️ Security Considerations**

### **Token Storage**
- **Frontend**: Store tokens in `localStorage` or secure cookies
- **Backend**: Validate tokens on every request
- **Mobile**: Use secure keychain/keystore

### **Error Handling**
- Always handle token expiration gracefully
- Implement automatic token refresh
- Provide clear error messages to users

### **Best Practices**
- Never log tokens or sensitive data
- Use HTTPS in production
- Implement proper CORS configuration
- Validate all user inputs
- Use rate limiting for authentication endpoints

---

## **🔧 Troubleshooting**

### **Common Issues**

**1. Token Validation Fails**
- Verify JWT secret matches Identity Service
- Check token expiration
- Ensure proper Bearer token format

**2. CORS Issues**
- Configure CORS in your frontend
- Check allowed origins in Identity Service

**3. User Not Found**
- Verify user exists in Identity Service
- Check email verification status

### **Debug Endpoints**
Use these endpoints to debug integration issues:

```bash
# Check token validity
curl -X GET "https://raposa-identity-production.up.railway.app/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Health check
curl -X GET "https://raposa-identity-production.up.railway.app/health/"
```

---

## **📞 Support**

### **Documentation**
- **Event Messages**: `REDIS_EVENT_MESSAGES.md`
- **API Documentation**: Visit `/docs` endpoint for interactive docs
- **Health Status**: Monitor `/health/` endpoint

### **Monitoring**
- **Redis Events**: Subscribe to `domain_events` channel
- **API Health**: Regular health check requests
- **Error Tracking**: Monitor authentication failures

This guide provides everything you need to integrate your service with the Raposa Identity Service! 🚀

For specific implementation questions or custom requirements, refer to the codebase or create integration tests following the patterns above.
