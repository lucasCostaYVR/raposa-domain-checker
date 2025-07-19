# DNS Analysis and Security Instructions

## DNS Analysis Development Workflow

### Using Development Scripts for DNS Features
When developing DNS analysis features, use the provided scripts:

```bash
# Start development environment
./scripts/dev.sh session           # Sets up environment with all dependencies

# Test DNS analysis locally
./scripts/dev.sh start             # Start dev server
curl -X POST http://localhost:8000/check-domain 
  -H "Content-Type: application/json" 
  -d '{"domain": "example.com", "email": "test@example.com"}'

# Code quality for DNS modules
./scripts/dev.sh format            # Format dns_utils.py and related files
./scripts/dev.sh lint              # Lint DNS analysis code
./scripts/dev.sh tests             # Run DNS analysis tests
```

### Feature Development Pattern for DNS Analysis
```bash
# 1. Start new DNS feature
./scripts/git.sh feature dns-analysis-improvement

# 2. Develop and test DNS functionality
./scripts/dev.sh start
# Modify src/dns_utils.py, test with sample domains

# 3. Deploy to staging for testing
./scripts/git.sh commit "Improve DNS analysis accuracy"
./scripts/git.sh finish-feature    # Test on stage.domainchecker.raposa.tech

# 4. Deploy to production
./scripts/git.sh release           # Deploy to api.domainchecker.raposa.tech
```

## DNS Security Analysis Patterns

### DNS Utilities Development

#### DNS Record Checking Structure
```python
import dns.resolver
import re
import asyncio
from typing import Dict, List, Optional, Any

class DNSAnalyzer:
    """Comprehensive DNS record analysis for domain security."""
    
    def __init__(self):
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 10
        self.resolver.lifetime = 30
    
    async def check_all_dns_records(self, domain: str) -> Dict[str, Any]:
        """Perform comprehensive DNS analysis."""
        results = {
            "domain": domain,
            "mx": await self.check_mx_records(domain),
            "spf": await self.check_spf_record(domain),
            "dkim": await self.check_dkim_record(domain),
            "dmarc": await self.check_dmarc_record(domain),
            "total_score": 0,
            "grade": "F",
            "issues": [],
            "recommendations": [],
            "security_summary": {}
        }
        
        # Calculate overall security score
        results.update(self._calculate_security_score(results))
        return results
```

#### MX Record Analysis
```python
async def check_mx_records(self, domain: str) -> Dict[str, Any]:
    """Analyze MX records for email security."""
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        
        mx_data = []
        for mx in mx_records:
            mx_info = {
                "priority": mx.preference,
                "exchange": str(mx.exchange).rstrip('.'),
                "security_features": await self._analyze_mx_security(str(mx.exchange))
            }
            mx_data.append(mx_info)
        
        # Sort by priority
        mx_data.sort(key=lambda x: x['priority'])
        
        return {
            "found": True,
            "records": mx_data,
            "count": len(mx_data),
            "score": self._score_mx_records(mx_data),
            "issues": self._identify_mx_issues(mx_data),
            "recommendations": self._get_mx_recommendations(mx_data)
        }
        
    except dns.resolver.NXDOMAIN:
        return self._no_record_result("MX", "No MX records found - email delivery will fail")
    except Exception as e:
        return self._error_result("MX", str(e))
```

#### SPF Record Analysis
```python
async def check_spf_record(self, domain: str) -> Dict[str, Any]:
    """Analyze SPF record for email authentication."""
    try:
        txt_records = dns.resolver.resolve(domain, 'TXT')
        spf_record = None
        
        for record in txt_records:
            text = str(record).strip('"')
            if text.startswith('v=spf1'):
                spf_record = text
                break
        
        if not spf_record:
            return self._no_record_result("SPF", "No SPF record found - emails may be marked as spam")
        
        # Parse SPF mechanisms
        mechanisms = self._parse_spf_mechanisms(spf_record)
        
        return {
            "found": True,
            "record": spf_record,
            "mechanisms": mechanisms,
            "score": self._score_spf_record(spf_record, mechanisms),
            "issues": self._identify_spf_issues(spf_record, mechanisms),
            "recommendations": self._get_spf_recommendations(mechanisms)
        }
        
    except Exception as e:
        return self._error_result("SPF", str(e))

def _parse_spf_mechanisms(self, spf_record: str) -> List[Dict[str, str]]:
    """Parse SPF record mechanisms."""
    mechanisms = []
    parts = spf_record.split()
    
    for part in parts[1:]:  # Skip 'v=spf1'
        if part in ['~all', '-all', '+all', '?all']:
            mechanisms.append({"type": "all", "qualifier": part[0], "value": part})
        elif part.startswith('include:'):
            mechanisms.append({"type": "include", "value": part[8:]})
        elif part.startswith('a:') or part == 'a':
            mechanisms.append({"type": "a", "value": part[2:] if ':' in part else ""})
        elif part.startswith('mx:') or part == 'mx':
            mechanisms.append({"type": "mx", "value": part[3:] if ':' in part else ""})
        elif part.startswith('ip4:'):
            mechanisms.append({"type": "ip4", "value": part[4:]})
        elif part.startswith('ip6:'):
            mechanisms.append({"type": "ip6", "value": part[4:]})
    
    return mechanisms
```

#### DKIM Record Analysis
```python
async def check_dkim_record(self, domain: str) -> Dict[str, Any]:
    """Analyze DKIM records for email authentication."""
    # Common DKIM selectors to check
    selectors = ['default', 'google', 'k1', 'dkim', 'mail', 'email']
    
    dkim_records = []
    for selector in selectors:
        dkim_domain = f"{selector}._domainkey.{domain}"
        try:
            txt_records = dns.resolver.resolve(dkim_domain, 'TXT')
            for record in txt_records:
                text = str(record).strip('"')
                if 'p=' in text:  # DKIM public key
                    dkim_info = self._parse_dkim_record(text)
                    dkim_info['selector'] = selector
                    dkim_records.append(dkim_info)
        except:
            continue
    
    if not dkim_records:
        return self._no_record_result("DKIM", "No DKIM records found - emails may fail authentication")
    
    return {
        "found": True,
        "records": dkim_records,
        "count": len(dkim_records),
        "score": self._score_dkim_records(dkim_records),
        "issues": self._identify_dkim_issues(dkim_records),
        "recommendations": self._get_dkim_recommendations(dkim_records)
    }

def _parse_dkim_record(self, dkim_record: str) -> Dict[str, Any]:
    """Parse DKIM record components."""
    components = {}
    parts = dkim_record.split(';')
    
    for part in parts:
        if '=' in part:
            key, value = part.strip().split('=', 1)
            components[key] = value
    
    # Analyze key strength
    public_key = components.get('p', '')
    key_length = len(public_key) * 3 // 4 if public_key else 0  # Rough estimate
    
    return {
        "record": dkim_record,
        "version": components.get('v', ''),
        "key_type": components.get('k', 'rsa'),
        "hash_algorithms": components.get('h', 'sha256'),
        "public_key_length": key_length,
        "flags": components.get('t', ''),
        "services": components.get('s', '*')
    }
```

#### DMARC Record Analysis
```python
async def check_dmarc_record(self, domain: str) -> Dict[str, Any]:
    """Analyze DMARC record for email policy."""
    dmarc_domain = f"_dmarc.{domain}"
    
    try:
        txt_records = dns.resolver.resolve(dmarc_domain, 'TXT')
        dmarc_record = None
        
        for record in txt_records:
            text = str(record).strip('"')
            if text.startswith('v=DMARC1'):
                dmarc_record = text
                break
        
        if not dmarc_record:
            return self._no_record_result("DMARC", "No DMARC record found - email spoofing protection disabled")
        
        # Parse DMARC policy
        policy = self._parse_dmarc_policy(dmarc_record)
        
        return {
            "found": True,
            "record": dmarc_record,
            "policy": policy,
            "score": self._score_dmarc_policy(policy),
            "issues": self._identify_dmarc_issues(policy),
            "recommendations": self._get_dmarc_recommendations(policy)
        }
        
    except Exception as e:
        return self._error_result("DMARC", str(e))

def _parse_dmarc_policy(self, dmarc_record: str) -> Dict[str, str]:
    """Parse DMARC policy components."""
    policy = {}
    parts = dmarc_record.split(';')
    
    for part in parts:
        if '=' in part:
            key, value = part.strip().split('=', 1)
            policy[key] = value
    
    return {
        "version": policy.get('v', ''),
        "policy": policy.get('p', 'none'),
        "subdomain_policy": policy.get('sp', ''),
        "alignment_spf": policy.get('aspf', 'r'),
        "alignment_dkim": policy.get('adkim', 'r'),
        "percentage": policy.get('pct', '100'),
        "report_uri": policy.get('rua', ''),
        "forensic_uri": policy.get('ruf', '')
    }
```

### Security Scoring Algorithm

#### Overall Score Calculation
```python
def _calculate_security_score(self, results: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall domain security score."""
    # Weighted scoring system
    weights = {
        "mx": 0.20,    # 20% - Email delivery
        "spf": 0.30,   # 30% - Email authentication
        "dkim": 0.25,  # 25% - Message integrity
        "dmarc": 0.25  # 25% - Policy enforcement
    }
    
    total_score = 0
    for record_type, weight in weights.items():
        record_score = results[record_type].get("score", 0)
        total_score += record_score * weight
    
    # Determine grade
    grade = self._calculate_grade(total_score)
    
    # Generate security summary
    security_summary = self._generate_security_summary(results, total_score, grade)
    
    return {
        "total_score": round(total_score),
        "grade": grade,
        "security_summary": security_summary,
        "issues": self._collect_all_issues(results),
        "recommendations": self._collect_all_recommendations(results)
    }

def _calculate_grade(self, score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 90:
        return "A+"
    elif score >= 85:
        return "A"
    elif score >= 80:
        return "A-"
    elif score >= 75:
        return "B+"
    elif score >= 70:
        return "B"
    elif score >= 65:
        return "B-"
    elif score >= 60:
        return "C+"
    elif score >= 55:
        return "C"
    elif score >= 50:
        return "C-"
    elif score >= 45:
        return "D+"
    elif score >= 40:
        return "D"
    else:
        return "F"
```

### Security Issue Detection

#### Issue Identification Patterns
```python
def _identify_spf_issues(self, spf_record: str, mechanisms: List[Dict]) -> List[str]:
    """Identify potential SPF security issues."""
    issues = []
    
    # Check for too permissive policies
    if '+all' in spf_record:
        issues.append("SPF record allows all senders (+all) - highly insecure")
    elif '?all' in spf_record:
        issues.append("SPF record has neutral policy (?all) - provides minimal protection")
    
    # Check for too many include mechanisms
    include_count = len([m for m in mechanisms if m.get("type") == "include"])
    if include_count > 10:
        issues.append(f"Too many include mechanisms ({include_count}) - may cause DNS lookup failures")
    
    # Check for missing 'all' mechanism
    all_mechanisms = [m for m in mechanisms if m.get("type") == "all"]
    if not all_mechanisms:
        issues.append("SPF record missing 'all' mechanism - unclear policy")
    
    return issues

def _identify_dmarc_issues(self, policy: Dict[str, str]) -> List[str]:
    """Identify potential DMARC security issues."""
    issues = []
    
    # Check policy strength
    if policy.get("policy") == "none":
        issues.append("DMARC policy set to 'none' - no enforcement action taken")
    
    # Check percentage
    percentage = int(policy.get("percentage", "100"))
    if percentage < 100:
        issues.append(f"DMARC policy only applies to {percentage}% of emails")
    
    # Check for reporting
    if not policy.get("report_uri"):
        issues.append("No DMARC reporting configured - missing visibility into email abuse")
    
    return issues
```

### Recommendation Engine

#### Security Recommendations
```python
def _get_spf_recommendations(self, mechanisms: List[Dict]) -> List[str]:
    """Generate SPF improvement recommendations."""
    recommendations = []
    
    # Check for strict policy
    all_mechanisms = [m for m in mechanisms if m.get("type") == "all"]
    if not all_mechanisms or all_mechanisms[0].get("qualifier", '+') != '-':
        recommendations.append("Consider using '-all' for strict SPF policy to reject unauthorized senders")
    
    # Check for IP-based mechanisms
    has_ip = any(m.get("type") in ["ip4", "ip6"] for m in mechanisms)
    if not has_ip:
        recommendations.append("Consider adding specific IP addresses (ip4:/ip6:) for better security")
    
    return recommendations

def _get_dmarc_recommendations(self, policy: Dict[str, str]) -> List[str]:
    """Generate DMARC improvement recommendations."""
    recommendations = []
    
    # Policy enforcement
    if policy.get("policy") in ["none", ""]:
        recommendations.append("Upgrade DMARC policy to 'quarantine' or 'reject' for better protection")
    elif policy.get("policy") == "quarantine":
        recommendations.append("Consider upgrading DMARC policy to 'reject' for maximum protection")
    
    # Reporting
    if not policy.get("report_uri"):
        recommendations.append("Configure DMARC reporting (rua=) to monitor email authentication")
    
    # Alignment
    if policy.get("alignment_spf") == "r":
        recommendations.append("Consider strict SPF alignment (aspf=s) for enhanced security")
    
    return recommendations
```

Remember to handle DNS timeouts gracefully and provide meaningful error messages for users when DNS lookups fail.
