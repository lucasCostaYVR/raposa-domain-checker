# 🔐 **Raposa Domain Checker - Frontend Integration Guide**

## **Overview**
This guide documents the authentication and domain management API endpoints for frontend integration. The API now supports user authentication via the Raposa Identity Service and full domain management capabilities for registered users.

### **Base URL**
- **Development**: `http://localhost:8000`
- **Staging**: `https://stage.domainchecker.raposa.tech`
- **Production**: `https://api.domainchecker.raposa.tech`

---

## **🔑 Authentication Endpoints**

### **1. User Registration**
Register a new user account.

**Endpoint**: `POST /auth/register`

```javascript
const response = await fetch('/auth/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'VerySecureP@ssw0rd2025!',
    first_name: 'John',
    last_name: 'Doe'
  })
});

const data = await response.json();
// Returns: { access_token, user }
```

**Request Body**:
```typescript
{
  email: string;          // Valid email address
  password: string;       // Strong password required
  first_name: string;     // User's first name
  last_name: string;      // User's last name
}
```

**Response**:
```typescript
{
  access_token: string;   // JWT token for authentication
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    email_verified: boolean;
    subscription_tier: string;
    created_at: string;
  }
}
```

### **2. User Login**
Authenticate existing user.

**Endpoint**: `POST /auth/login`

```javascript
const response = await fetch('/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'VerySecureP@ssw0rd2025!'
  })
});

const data = await response.json();
// Store the access_token for subsequent requests
localStorage.setItem('access_token', data.access_token);
```

**Request Body**:
```typescript
{
  email: string;
  password: string;
}
```

**Response**: Same as registration response.

### **3. Get User Profile**
Get current user's profile information.

**Endpoint**: `GET /auth/profile`
**Authentication**: Required

```javascript
const response = await fetch('/auth/profile', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});

const profile = await response.json();
```

**Response**:
```typescript
{
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  email_verified: boolean;
  subscription_tier: string;
  created_at: string;
  last_login: string | null;
}
```

---

## **🏠 Domain Management Endpoints**

### **1. List User Domains**
Get all domains managed by the current user.

**Endpoint**: `GET /domains/`
**Authentication**: Required

```javascript
const response = await fetch('/domains/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});

const domains = await response.json();
```

**Response**:
```typescript
Array<{
  id: number;
  domain: string;
  display_name: string | null;
  is_verified: boolean;
  auto_check_enabled: boolean;
  check_frequency: 'weekly' | 'monthly';
  last_auto_check: string | null;
  created_at: string;
  updated_at: string | null;
}>
```

### **2. Add Domain**
Add a new domain to user's managed domains.

**Endpoint**: `POST /domains/`
**Authentication**: Required

```javascript
const response = await fetch('/domains/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  },
  body: JSON.stringify({
    domain: 'example.com',
    description: 'My company website'
  })
});

const newDomain = await response.json();
```

**Request Body**:
```typescript
{
  domain: string;         // Domain name (e.g., "example.com")
  description?: string;   // Optional description
}
```

**Response**: Domain object (same structure as in list response).

### **3. Update Domain**
Update domain settings.

**Endpoint**: `PUT /domains/{domain_id}`
**Authentication**: Required

```javascript
const response = await fetch(`/domains/${domainId}`, {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  },
  body: JSON.stringify({
    display_name: 'Company Website',
    auto_check_enabled: true,
    check_frequency: 'weekly'
  })
});

const updatedDomain = await response.json();
```

**Request Body**:
```typescript
{
  display_name?: string;
  auto_check_enabled?: boolean;
  check_frequency?: 'weekly' | 'monthly';
}
```

**Response**: Updated domain object.

### **4. Delete Domain**
Remove a domain from user's managed domains.

**Endpoint**: `DELETE /domains/{domain_id}`
**Authentication**: Required

```javascript
const response = await fetch(`/domains/${domainId}`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});

// Returns 204 No Content on success
```

### **5. Run Domain Check**
Perform security analysis on a managed domain.

**Endpoint**: `POST /domains/{domain_id}/check`
**Authentication**: Required

```javascript
const response = await fetch(`/domains/${domainId}/check`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});

const checkResult = await response.json();
```

**Response**:
```typescript
{
  id: number;
  email: string;
  domain: string;
  mx_record: {
    records: Array<{ preference: number; exchange: string }>;
    status: string;
    issues: string[];
    score: number;
    explanation: {
      what_is: string;
      current_status: string;
      risk_if_misconfigured: string;
    };
  };
  spf_record: {
    record: string;
    status: string;
    mechanisms: string[];
    issues: string[];
    score: number;
    explanation: object;
  };
  dkim_record: {
    selectors: object;
    status: string;
    issues: string[];
    score: number;
    explanation: object;
  };
  dmarc_record: {
    record: string;
    status: string;
    policy: object;
    issues: string[];
    score: number;
    explanation: object;
  };
  score: number | null;
  grade: string;
  issues: string[];
  recommendations: string[];
  security_summary: {
    security_level: string;
    overall_message: string;
    components_configured: string;
    grade_meaning: string;
    priority_actions: string[];
    protection_status: {
      spoofing_protection: string;
      email_delivery: string;
      authentication: string;
    };
  };
  created_at: string;
  opt_in_marketing: boolean;
}
```

### **6. Get Domain Check History**
Get historical check results for a domain.

**Endpoint**: `GET /domains/{domain_id}/history`
**Authentication**: Required
**Query Parameters**: `page` (default: 1), `per_page` (default: 20)

```javascript
const response = await fetch(`/domains/${domainId}/history?page=1&per_page=10`, {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});

const history = await response.json();
```

**Response**:
```typescript
{
  checks: Array<DomainCheckResult>;  // Same structure as single check
  total_count: number;
  page: number;
  per_page: number;
  has_next: boolean;
  has_prev: boolean;
}
```

---

## **🔓 Anonymous Domain Check**

### **Anonymous Domain Check**
Check a domain without authentication (rate limited).

**Endpoint**: `POST /check-domain`
**Authentication**: Not required
**Rate Limit**: 1 check per domain per month per IP

```javascript
const response = await fetch('/check-domain', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    domain: 'example.com',
    email: 'optional@example.com'  // Optional for additional checks
  })
});

const result = await response.json();
```

**Request Body**:
```typescript
{
  domain: string;
  email?: string;  // Required for additional checks beyond rate limit
}
```

**Response**: Same structure as authenticated domain check.

---

## **🛠️ Frontend Implementation Examples**

### **Authentication Helper Functions**

```javascript
class AuthService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  }

  // Store token
  setToken(token) {
    localStorage.setItem('access_token', token);
  }

  // Get stored token
  getToken() {
    return localStorage.getItem('access_token');
  }

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.getToken();
  }

  // Make authenticated request
  async authenticatedFetch(url, options = {}) {
    const token = this.getToken();
    return fetch(`${this.baseURL}${url}`, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${token}`
      }
    });
  }

  // Login
  async login(email, password) {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (response.ok) {
      const data = await response.json();
      this.setToken(data.access_token);
      return data;
    }
    
    throw new Error('Login failed');
  }

  // Register
  async register(userData) {
    const response = await fetch(`${this.baseURL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    });

    if (response.ok) {
      const data = await response.json();
      this.setToken(data.access_token);
      return data;
    }
    
    throw new Error('Registration failed');
  }

  // Logout
  logout() {
    localStorage.removeItem('access_token');
  }

  // Get profile
  async getProfile() {
    const response = await this.authenticatedFetch('/auth/profile');
    if (response.ok) {
      return response.json();
    }
    throw new Error('Failed to get profile');
  }
}
```

### **Domain Management Helper Functions**

```javascript
class DomainService {
  constructor(authService) {
    this.auth = authService;
  }

  // Get user domains
  async getDomains() {
    const response = await this.auth.authenticatedFetch('/domains/');
    if (response.ok) {
      return response.json();
    }
    throw new Error('Failed to get domains');
  }

  // Add domain
  async addDomain(domain, description) {
    const response = await this.auth.authenticatedFetch('/domains/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ domain, description })
    });

    if (response.ok) {
      return response.json();
    }
    throw new Error('Failed to add domain');
  }

  // Update domain
  async updateDomain(domainId, updates) {
    const response = await this.auth.authenticatedFetch(`/domains/${domainId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    });

    if (response.ok) {
      return response.json();
    }
    throw new Error('Failed to update domain');
  }

  // Delete domain
  async deleteDomain(domainId) {
    const response = await this.auth.authenticatedFetch(`/domains/${domainId}`, {
      method: 'DELETE'
    });

    if (!response.ok) {
      throw new Error('Failed to delete domain');
    }
  }

  // Run domain check
  async checkDomain(domainId) {
    const response = await this.auth.authenticatedFetch(`/domains/${domainId}/check`, {
      method: 'POST'
    });

    if (response.ok) {
      return response.json();
    }
    throw new Error('Failed to check domain');
  }

  // Get domain history
  async getDomainHistory(domainId, page = 1, perPage = 20) {
    const response = await this.auth.authenticatedFetch(
      `/domains/${domainId}/history?page=${page}&per_page=${perPage}`
    );

    if (response.ok) {
      return response.json();
    }
    throw new Error('Failed to get domain history');
  }
}
```

### **React Hook Example**

```javascript
import { useState, useEffect } from 'react';

function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const authService = new AuthService();

  useEffect(() => {
    const loadUser = async () => {
      if (authService.isAuthenticated()) {
        try {
          const profile = await authService.getProfile();
          setUser(profile);
        } catch (error) {
          authService.logout();
        }
      }
      setLoading(false);
    };

    loadUser();
  }, []);

  const login = async (email, password) => {
    const data = await authService.login(email, password);
    setUser(data.user);
    return data;
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  return { user, loading, login, logout, isAuthenticated: !!user };
}
```

---

## **⚠️ Error Handling**

### **Common HTTP Status Codes**
- `200` - Success
- `201` - Created (for POST requests)
- `204` - No Content (for DELETE requests)
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid/expired token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (validation errors)
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

### **Error Response Format**
```typescript
{
  detail: string | Array<{
    type: string;
    loc: string[];
    msg: string;
    input: any;
  }>;
}
```

### **Rate Limiting Responses**
When rate limited, anonymous users receive:
```json
{
  "detail": "You've already checked this domain this month. Provide an email address for additional checks!"
}
```

---

## **🔐 Security Best Practices**

1. **Token Storage**: Store JWT tokens securely (consider httpOnly cookies for production)
2. **Token Expiration**: Handle token expiration gracefully with refresh logic
3. **HTTPS**: Always use HTTPS in production
4. **Input Validation**: Validate all user inputs on the frontend
5. **Error Handling**: Don't expose sensitive information in error messages

---

## **🚀 Quick Integration Checklist**

- [ ] Implement authentication service with login/register/logout
- [ ] Add JWT token storage and management
- [ ] Create domain management interface
- [ ] Implement domain check functionality with results display
- [ ] Add pagination for domain history
- [ ] Handle rate limiting for anonymous users
- [ ] Add proper error handling and user feedback
- [ ] Implement responsive design for all new features
- [ ] Test all authentication flows
- [ ] Test domain management CRUD operations

This API provides a complete foundation for building a secure, user-friendly domain security analysis application! 🎉
