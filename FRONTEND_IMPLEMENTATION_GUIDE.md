# Frontend Implementation Guide - Raposa Domain Checker

## Project Overview
Build a modern, responsive frontend for the Raposa Domain Checker that allows users to check domain security configurations and receive detailed email reports. The backend API is fully functional and deployed at `https://raposa-app-api-production.up.railway.app`.

**🚀 CORS Configured**: The production API is configured to accept requests from `http://localhost:3000` for frontend development.

## User Flow & API Integration Guide

### 🎯 **Primary User Journey**
1. **Landing Page** - User enters domain and email
2. **Domain Validation** - Real-time validation and submission
3. **Analysis In Progress** - Loading state while DNS analysis runs (2-5 seconds)
4. **Results Display** - Show comprehensive security analysis
5. **Email Confirmation** - Confirm email report sent

---

## 📋 **API Endpoints Documentation**

### **Base URL**: `https://raposa-app-api-production.up.railway.app`

### 1. **Health Check** *(Optional - for status monitoring)*
```http
GET /healthz/
```

**Response:**
```json
{
  "status": "ok"
}
```

---

### 2. **API Information** *(Optional - for version display)*
```http
GET /
```

**Response:**
```json
{
  "message": "Raposa Domain Checker API",
  "version": "1.0.0"
}
```

---

### 3. **Domain Security Check** *(Primary endpoint)*
```http
POST /check-domain
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "domain": "github.com",
  "opt_in_marketing": false
}
```

**Response (Success - 200):**
```json
{
  "id": 6,
  "email": "user@example.com",
  "domain": "github.com",
  "mx_record": {
    "records": [
      {"preference": 1, "exchange": "aspmx.l.google.com"},
      {"preference": 5, "exchange": "alt1.aspmx.l.google.com"},
      {"preference": 5, "exchange": "alt2.aspmx.l.google.com"},
      {"preference": 10, "exchange": "alt3.aspmx.l.google.com"},
      {"preference": 10, "exchange": "alt4.aspmx.l.google.com"}
    ],
    "status": "valid",
    "issues": [],
    "score": 20
  },
  "spf_record": {
    "record": "v=spf1 ip4:192.30.252.0/22 include:_netblocks.google.com ~all",
    "status": "warning",
    "mechanisms": ["ip4:192.30.252.0/22", "include:_netblocks.google.com", "~all"],
    "issues": ["Unknown SPF mechanism detected"],
    "score": 20
  },
  "dkim_record": {
    "selectors": {
      "google": {
        "record": "v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0...",
        "selector": "google",
        "status": "valid",
        "key_details": {
          "v": "DKIM1",
          "k": "rsa",
          "p": "MIIBIjANBgkqhkiG9w0..."
        },
        "issues": [],
        "score": 15
      }
    },
    "status": "basic",
    "issues": ["Consider adding multiple DKIM selectors for redundancy"],
    "score": 15
  },
  "dmarc_record": {
    "record": "v=DMARC1; p=reject; pct=100; rua=mailto:dmarc@github.com",
    "status": "valid",
    "policy": {
      "v": "DMARC1",
      "p": "reject",
      "pct": "100",
      "rua": "mailto:dmarc@github.com"
    },
    "issues": [],
    "score": 30
  },
  "score": 85,
  "grade": "A",
  "issues": [
    "Unknown SPF mechanism detected",
    "Consider adding multiple DKIM selectors for redundancy"
  ],
  "recommendations": [
    "Add multiple DKIM selectors for redundancy and better security",
    "Complete email security setup with all four components: MX, SPF, DKIM, and DMARC"
  ],
  "opt_in_marketing": false,
  "created_at": "2025-07-16T02:52:56.226942Z"
}
```

**Error Responses:**

*Invalid Domain (422):*
```json
{
  "detail": "Invalid or unsafe domain format"
}
```

*Rate Limit Exceeded (429):*
```json
{
  "detail": "Domain check limit exceeded. Maximum 5 checks per domain per month."
}
```

*Server Error (500):*
```json
{
  "detail": "Internal server error during domain analysis"
}
```

---

## 🎨 **Frontend Implementation Requirements**

### **Technology Stack Recommendations**
- **Framework**: React, Vue.js, or Next.js
- **Styling**: Tailwind CSS or Material-UI
- **HTTP Client**: Axios or Fetch API
- **State Management**: React Context/Redux or Vuex
- **Form Validation**: React Hook Form or Vuelidate

### **Key Components to Build**

#### 1. **Landing Page Component**
```jsx
// Components needed:
- HeroSection (domain input form)
- SecurityScoreDisplay (sample results)
- FeaturesList (what we analyze)
- TestimonialsSection (optional)
- Footer
```

#### 2. **Domain Check Form**
```jsx
// Form fields:
- Domain input (with validation)
- Email input (with validation)
- Marketing opt-in checkbox
- Submit button with loading state
```

#### 3. **Results Display Component**
```jsx
// Results sections:
- Overall Score & Grade (prominent display)
- Component Breakdown (MX, SPF, DKIM, DMARC)
- Issues List (with severity indicators)
- Recommendations (actionable items)
- Email Confirmation Message
```

#### 4. **Loading/Progress Component**
```jsx
// Loading states:
- DNS analysis in progress
- Progress indicators
- Estimated completion time (2-5 seconds)
- Animated security icons
```

---

## 🔄 **Detailed User Flow Implementation**

### **Step 1: Landing Page**
**Purpose**: Capture user interest and collect domain + email

**API Calls**: None (static content)

**UI Elements**:
- Hero section with domain input
- Email input field
- Marketing opt-in checkbox
- "Analyze Domain Security" CTA button
- Sample security score visualization

### **Step 2: Form Validation & Submission**
**Purpose**: Validate inputs and submit for analysis

**Frontend Validation**:
```javascript
// Domain validation regex
const domainRegex = /^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$/;

// Email validation
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Validation rules
- Domain: Required, valid format, not localhost/private IPs
- Email: Required, valid email format
- Marketing opt-in: Boolean (defaults to false)
```

**API Call**:
```javascript
const submitDomainCheck = async (formData) => {
  try {
    const response = await fetch('https://raposa-app-api-production.up.railway.app/check-domain', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: formData.email,
        domain: formData.domain,
        opt_in_marketing: formData.optInMarketing
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Analysis failed');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Domain check failed:', error);
    throw error;
  }
};
```

### **Step 3: Loading State**
**Purpose**: Show progress while analysis runs (typically 2-5 seconds)

**API Calls**: None (waiting for response)

**UI Elements**:
- Loading spinner or progress bar
- "Analyzing domain security..." message
- DNS component analysis steps
- Animated security shield/lock icons

### **Step 4: Results Display**
**Purpose**: Show comprehensive security analysis

**API Calls**: None (display response data)

**UI Sections**:

#### **Overall Score Display**
```jsx
// Grade color mapping
const gradeColors = {
  'A+': '#28a745', 'A': '#28a745', 'A-': '#28a745',
  'B+': '#17a2b8', 'B': '#17a2b8', 'B-': '#17a2b8', 
  'C+': '#ffc107', 'C': '#ffc107', 'C-': '#ffc107',
  'D+': '#fd7e14', 'D': '#fd7e14', 'D-': '#fd7e14',
  'F': '#dc3545'
};

// Display: Large score (85/100), Grade (A), Color-coded
```

#### **Component Breakdown**
```jsx
// For each component (MX, SPF, DKIM, DMARC):
- Component name & icon
- Status indicator (✅ Valid, ⚠️ Warning, ❌ Invalid)
- Individual score (e.g., "20/25 points")
- Brief description of findings
- Expandable details section
```

#### **Issues & Recommendations**
```jsx
// Issues section:
- List of identified problems
- Severity indicators (Critical, Warning, Info)
- Technical details for each issue

// Recommendations section:
- Actionable improvement steps
- Priority indicators
- Implementation difficulty estimates
```

### **Step 5: Email Confirmation**
**Purpose**: Confirm email report delivery

**API Calls**: None (automatic background process)

**UI Elements**:
- Success message: "Detailed report sent to [email]"
- Email delivery confirmation
- "Check your inbox" guidance
- Option to check another domain

---

## 🎨 **UI/UX Design Guidelines**

### **Color Scheme**
```css
/* Security-focused color palette */
:root {
  --primary-blue: #007bff;
  --success-green: #28a745;
  --warning-yellow: #ffc107;
  --danger-red: #dc3545;
  --info-cyan: #17a2b8;
  --dark-gray: #343a40;
  --light-gray: #f8f9fa;
}
```

### **Typography**
- **Headers**: Bold, security-focused fonts (Inter, Roboto)
- **Body**: Clear, readable fonts for technical content
- **Code**: Monospace fonts for DNS records

### **Component Status Icons**
```jsx
const StatusIcon = ({ status }) => {
  const icons = {
    'valid': '✅',
    'warning': '⚠️', 
    'invalid': '❌',
    'unknown': '❓'
  };
  return icons[status] || '❓';
};
```

### **Responsive Design**
- **Mobile-first** approach
- **Breakpoints**: 320px, 768px, 1024px, 1200px
- **Key considerations**: 
  - Stack components vertically on mobile
  - Ensure form inputs are touch-friendly
  - Optimize loading states for mobile

---

## 🔧 **Error Handling**

### **Error States to Handle**
```javascript
const ErrorHandler = {
  // Network errors
  NETWORK_ERROR: 'Unable to connect. Please check your internet connection.',
  
  // Validation errors
  INVALID_DOMAIN: 'Please enter a valid domain name (e.g., example.com)',
  INVALID_EMAIL: 'Please enter a valid email address',
  
  // API errors
  RATE_LIMITED: 'You\'ve reached the monthly limit for this domain. Try again next month.',
  SERVER_ERROR: 'Analysis failed. Please try again in a few moments.',
  
  // Timeout errors
  TIMEOUT: 'Analysis is taking longer than expected. Please try again.'
};
```

### **Error Display Components**
```jsx
// Error message component
const ErrorMessage = ({ error, onRetry }) => (
  <div className="error-container">
    <span className="error-icon">⚠️</span>
    <p className="error-text">{error.message}</p>
    {onRetry && <button onClick={onRetry}>Try Again</button>}
  </div>
);
```

---

## 📱 **Sample Component Architecture**

### **Main App Structure**
```jsx
App/
├── components/
│   ├── Header/
│   ├── DomainCheckForm/
│   ├── LoadingState/
│   ├── ResultsDisplay/
│   │   ├── ScoreCard/
│   │   ├── ComponentBreakdown/
│   │   ├── IssuesList/
│   │   └── Recommendations/
│   ├── ErrorMessage/
│   └── Footer/
├── services/
│   └── api.js
├── utils/
│   └── validation.js
└── styles/
    └── main.css
```

### **State Management Example**
```javascript
// Application state structure
const AppState = {
  // Form data
  formData: {
    domain: '',
    email: '',
    optInMarketing: false
  },
  
  // UI state
  isLoading: false,
  error: null,
  
  // Results
  analysisResults: null,
  emailSent: false
};
```

---

## 🚀 **Deployment Considerations**

### **Environment Variables**
```javascript
// Frontend environment variables
const CONFIG = {
  API_BASE_URL: process.env.REACT_APP_API_URL || 'https://raposa-app-api-production.up.railway.app',
  ENVIRONMENT: process.env.NODE_ENV || 'development'
};
```

### **CORS Configuration**
✅ **Already Configured**: The production API accepts requests from:
- `http://localhost:3000` (React development server)
- `http://127.0.0.1:3000` (Alternative localhost)

No additional CORS configuration needed on the frontend side.

### **SEO Optimization**
- **Meta tags** for domain security checking
- **Open Graph** tags for social sharing
- **Structured data** for search engines
- **Fast loading** with code splitting
- **Mobile optimization** for Google rankings

### **Analytics Tracking** *(Optional)*
```javascript
// Recommended events to track
const Analytics = {
  DOMAIN_CHECK_STARTED: 'domain_check_started',
  DOMAIN_CHECK_COMPLETED: 'domain_check_completed', 
  EMAIL_SUBMITTED: 'email_submitted',
  ERROR_OCCURRED: 'error_occurred'
};
```

---

## 📋 **Testing Strategy**

### **Unit Tests**
- Form validation functions
- API service functions
- Component rendering
- Error handling logic

### **Integration Tests**
- Full user flow (form submission → results)
- API integration
- Error scenarios
- Loading states

### **E2E Tests**
- Complete user journey
- Mobile responsiveness
- Cross-browser compatibility
- Performance testing

---

## 🔍 **Sample Implementation Code**

### **Domain Check Form Component**
```jsx
import React, { useState } from 'react';

const DomainCheckForm = ({ onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    domain: '',
    email: '',
    optInMarketing: false
  });
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};
    
    // Domain validation
    const domainRegex = /^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$/;
    if (!formData.domain) {
      newErrors.domain = 'Domain is required';
    } else if (!domainRegex.test(formData.domain)) {
      newErrors.domain = 'Please enter a valid domain (e.g., example.com)';
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="domain-check-form">
      <div className="form-group">
        <label htmlFor="domain">Domain to Check</label>
        <input
          type="text"
          id="domain"
          placeholder="example.com"
          value={formData.domain}
          onChange={(e) => setFormData({...formData, domain: e.target.value})}
          className={errors.domain ? 'error' : ''}
        />
        {errors.domain && <span className="error-text">{errors.domain}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="email">Email for Report</label>
        <input
          type="email"
          id="email"
          placeholder="you@example.com"
          value={formData.email}
          onChange={(e) => setFormData({...formData, email: e.target.value})}
          className={errors.email ? 'error' : ''}
        />
        {errors.email && <span className="error-text">{errors.email}</span>}
      </div>

      <div className="form-group">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={formData.optInMarketing}
            onChange={(e) => setFormData({...formData, optInMarketing: e.target.checked})}
          />
          Send me security tips and updates
        </label>
      </div>

      <button type="submit" disabled={isLoading} className="submit-button">
        {isLoading ? 'Analyzing...' : 'Check Domain Security'}
      </button>
    </form>
  );
};

export default DomainCheckForm;
```

---

## 📞 **Support & Communication**

### **Backend API Contact**
- **Production URL**: `https://raposa-app-api-production.up.railway.app`
- **API Documentation**: Available at `/docs` endpoint
- **Health Check**: Available at `/healthz` endpoint
- **CORS**: Configured for `localhost:3000` development

### **Expected Response Times**
- **Domain Analysis**: 2-5 seconds typically
- **Email Delivery**: 10-30 seconds (background process)
- **API Availability**: 99.9% uptime target

### **Rate Limits**
- **5 checks per domain per month** (calendar month)
- **No per-IP rate limiting** currently implemented
- **Graceful degradation** on limit exceeded

### **Core Features Implemented**
✅ **Domain Security Analysis**: MX, SPF, DKIM, DMARC records  
✅ **Intelligent Scoring**: 0-100 points with A-F grades  
✅ **Email Reports**: HTML email delivery via Brevo  
✅ **Background Processing**: Non-blocking email sending  
✅ **Error Handling**: Comprehensive error responses  
✅ **CORS Support**: Ready for frontend development  

---

This guide covers the **core functionality** that is fully implemented and tested. The backend API is production-ready and waiting for your frontend!
