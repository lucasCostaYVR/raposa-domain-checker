"""
DNS utility functions for domain security analysis.
Handles MX, SPF, DKIM, DMARC, and other email security record checks.
"""

import dns.resolver
import dns.exception
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Common DKIM selectors to check
COMMON_DKIM_SELECTORS = [
    'default',
    'google',
    'amazonses', 
    'mailchimp',
    'sendgrid',
    'mailgun',
    'constantcontact',
    'awsses',
    'postmark',
    'mandrill',
    'sparkpost',
    'sendinblue',
    'outlook',
    'office365'
]

class DNSQueryError(Exception):
    """Custom exception for DNS query errors"""
    pass

async def query_dns_record(domain: str, record_type: str, timeout: int = 5) -> Optional[List[str]]:
    """
    Query DNS record with proper error handling and timeout.
    
    Args:
        domain: Domain name to query
        record_type: DNS record type (MX, TXT, etc.)
        timeout: Query timeout in seconds
        
    Returns:
        List of record strings or None if not found
    """
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout
        resolver.lifetime = timeout
        
        # Run DNS query in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, 
                lambda: resolver.resolve(domain, record_type)
            )
        
        return [str(record) for record in result]
        
    except dns.exception.Timeout:
        logger.warning(f"DNS timeout for {domain} ({record_type})")
        return None
    except dns.resolver.NXDOMAIN:
        logger.info(f"Domain not found: {domain}")
        return None
    except dns.resolver.NoAnswer:
        logger.debug(f"No {record_type} record found for {domain}")
        return None
    except Exception as e:
        logger.error(f"DNS query error for {domain} ({record_type}): {e}")
        return None

async def check_mx_records(domain: str) -> Dict[str, Any]:
    """
    Check MX records for a domain.
    
    Returns:
        Dict with MX record details, status, and issues
    """
    records = await query_dns_record(domain, 'MX')
    
    if not records:
        return {
            "records": [],
            "status": "missing",
            "issues": ["No MX records found - email delivery will fail"],
            "score": 0
        }
    
    # Parse MX records
    mx_list = []
    issues = []
    
    for record in records:
        try:
            # MX record format: "preference exchange"
            parts = record.split(' ', 1)
            if len(parts) == 2:
                preference = int(parts[0])
                exchange = parts[1].rstrip('.')
                mx_list.append({
                    "preference": preference,
                    "exchange": exchange
                })
            else:
                issues.append(f"Invalid MX record format: {record}")
        except ValueError:
            issues.append(f"Invalid MX record preference: {record}")
    
    # Check for common issues
    if any(mx["exchange"] == "." for mx in mx_list):
        issues.append("Null MX record found - domain explicitly rejects email")
        status = "null_mx"
        score = 0
    elif mx_list:
        status = "valid"
        score = 20
    else:
        status = "invalid"
        score = 0
        issues.append("No valid MX records found")
    
    return {
        "records": mx_list,
        "status": status,
        "issues": issues,
        "score": score
    }

async def check_spf_record(domain: str) -> Dict[str, Any]:
    """
    Check SPF record for a domain.
    
    Returns:
        Dict with SPF record details, mechanisms, and analysis
    """
    txt_records = await query_dns_record(domain, 'TXT')
    
    if not txt_records:
        return {
            "record": None,
            "status": "missing",
            "mechanisms": [],
            "issues": ["No SPF record found - increases spam risk"],
            "score": 0
        }
    
    # Find SPF record
    spf_record = None
    for record in txt_records:
        record_clean = record.strip('"')
        if record_clean.startswith('v=spf1'):
            spf_record = record_clean
            break
    
    if not spf_record:
        return {
            "record": None,
            "status": "missing",
            "mechanisms": [],
            "issues": ["No SPF record found - increases spam risk"],
            "score": 0
        }
    
    # Parse SPF mechanisms
    mechanisms = []
    issues = []
    score = 5  # Base score for having SPF
    
    # Split SPF record into mechanisms
    parts = spf_record.split()
    
    for part in parts[1:]:  # Skip 'v=spf1'
        if part.startswith(('ip4:', 'ip6:', 'a:', 'mx:', 'include:', 'exists:', 'ptr:')):
            mechanisms.append(part)
        elif part in ['~all', '-all', '?all', '+all']:
            mechanisms.append(part)
            # Score based on strictness
            if part == '-all':
                score += 20  # Strict fail
            elif part == '~all':
                score += 15  # Soft fail
            elif part == '?all':
                score += 5   # Neutral
                issues.append("Consider using '-all' for stricter SPF policy")
            elif part == '+all':
                score = max(score - 10, 0)  # Pass all (insecure)
                issues.append("'+all' allows any server to send email - very insecure")
        else:
            issues.append(f"Unknown SPF mechanism: {part}")
    
    # Check for common issues
    if not any(part.endswith('all') for part in parts):
        issues.append("SPF record missing 'all' mechanism")
        score = max(score - 5, 0)
    
    # Check for too many DNS lookups (SPF has 10 lookup limit)
    lookup_mechanisms = [m for m in mechanisms if m.startswith(('include:', 'a:', 'mx:', 'exists:', 'ptr:'))]
    if len(lookup_mechanisms) > 8:
        issues.append("SPF record may exceed DNS lookup limit (10)")
    
    status = "valid" if not issues else "warning"
    
    return {
        "record": spf_record,
        "status": status,
        "mechanisms": mechanisms,
        "issues": issues,
        "score": min(score, 25)  # Cap at 25 points
    }

async def check_dkim_records(domain: str, selectors: List[str] = None) -> Dict[str, Any]:
    """
    Check DKIM records for a domain using common selectors.
    
    Args:
        domain: Domain to check
        selectors: List of DKIM selectors to check (uses common ones if None)
        
    Returns:
        Dict with DKIM record details for each selector found
    """
    if selectors is None:
        selectors = COMMON_DKIM_SELECTORS
    
    found_selectors = {}
    issues = []
    total_score = 0
    
    # Check each selector concurrently
    tasks = []
    for selector in selectors:
        dkim_domain = f"{selector}._domainkey.{domain}"
        tasks.append(check_single_dkim_record(dkim_domain, selector))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Error checking DKIM selector {selectors[i]}: {result}")
            continue
        
        if result["record"]:
            found_selectors[selectors[i]] = result
            total_score += result["score"]
    
    # Overall DKIM assessment
    if not found_selectors:
        status = "missing"
        issues.append("No DKIM records found - emails may be marked as spam")
        score = 0
    elif len(found_selectors) == 1:
        status = "basic"
        score = min(total_score, 15)
        issues.append("Consider adding multiple DKIM selectors for redundancy")
    else:
        status = "good"
        score = min(total_score, 25)
    
    return {
        "selectors": found_selectors,
        "status": status,
        "issues": issues,
        "score": score
    }

async def check_single_dkim_record(dkim_domain: str, selector: str) -> Dict[str, Any]:
    """Check a single DKIM record for a specific selector."""
    txt_records = await query_dns_record(dkim_domain, 'TXT')
    
    if not txt_records:
        return {
            "record": None,
            "selector": selector,
            "status": "missing",
            "key_details": {},
            "issues": [],
            "score": 0
        }
    
    # Combine TXT records (DKIM can be split across multiple TXT records)
    dkim_record = ''.join(record.strip('"') for record in txt_records)
    
    # Parse DKIM record
    key_details = parse_dkim_record(dkim_record)
    issues = []
    score = 10  # Base score for having DKIM
    
    # Analyze key strength
    if key_details.get("k") == "rsa":
        # Try to determine key length from public key
        if "p" in key_details and key_details["p"]:
            # Rough estimation of key length based on base64 length
            key_data = key_details["p"].replace(" ", "")
            estimated_bits = len(key_data) * 6 // 8 * 8  # Rough estimate
            
            if estimated_bits >= 2048:
                score += 5
            elif estimated_bits >= 1024:
                issues.append("Consider upgrading to 2048-bit RSA key")
            else:
                issues.append("RSA key appears to be less than 1024 bits - upgrade recommended")
                score = max(score - 2, 0)
        else:
            issues.append("Empty or missing public key in DKIM record")
            score = 0
    
    # Check for test mode
    if key_details.get("t") == "y":
        issues.append("DKIM record is in test mode")
        score = max(score - 3, 0)
    
    status = "valid" if not issues else "warning"
    
    return {
        "record": dkim_record,
        "selector": selector,
        "status": status,
        "key_details": key_details,
        "issues": issues,
        "score": score
    }

def parse_dkim_record(record: str) -> Dict[str, str]:
    """Parse DKIM record into components."""
    components = {}
    
    # DKIM record format: tag=value; tag=value; ...
    pairs = record.split(';')
    
    for pair in pairs:
        if '=' in pair:
            tag, value = pair.split('=', 1)
            components[tag.strip()] = value.strip()
    
    return components

async def check_dmarc_record(domain: str) -> Dict[str, Any]:
    """
    Check DMARC record for a domain.
    
    Returns:
        Dict with DMARC policy details and analysis
    """
    dmarc_domain = f"_dmarc.{domain}"
    txt_records = await query_dns_record(dmarc_domain, 'TXT')
    
    if not txt_records:
        return {
            "record": None,
            "status": "missing",
            "policy": {},
            "issues": ["No DMARC record found - email authentication not enforced"],
            "score": 0
        }
    
    # Find DMARC record
    dmarc_record = None
    for record in txt_records:
        record_clean = record.strip('"')
        if record_clean.startswith('v=DMARC1'):
            dmarc_record = record_clean
            break
    
    if not dmarc_record:
        return {
            "record": None,
            "status": "missing",
            "policy": {},
            "issues": ["No valid DMARC record found"],
            "score": 0
        }
    
    # Parse DMARC record
    policy = parse_dmarc_record(dmarc_record)
    issues = []
    score = 10  # Base score for having DMARC
    
    # Analyze policy strength
    p_policy = policy.get("p", "none")
    if p_policy == "reject":
        score += 20
    elif p_policy == "quarantine":
        score += 15
        issues.append("Consider upgrading to 'p=reject' for maximum protection")
    elif p_policy == "none":
        score += 5
        issues.append("DMARC policy is 'none' - not enforcing authentication")
    
    # Check percentage
    pct = policy.get("pct", "100")
    try:
        pct_value = int(pct)
        if pct_value < 100:
            issues.append(f"DMARC policy applies to only {pct}% of emails")
            score = max(score - 5, 0)
    except ValueError:
        issues.append("Invalid DMARC percentage value")
    
    # Check for reporting
    if not policy.get("rua") and not policy.get("ruf"):
        issues.append("No DMARC reporting configured")
        score = max(score - 3, 0)
    
    status = "valid" if not issues else "warning"
    
    return {
        "record": dmarc_record,
        "status": status,
        "policy": policy,
        "issues": issues,
        "score": min(score, 30)  # Cap at 30 points
    }

def parse_dmarc_record(record: str) -> Dict[str, str]:
    """Parse DMARC record into components."""
    components = {}
    
    # DMARC record format: tag=value; tag=value; ...
    pairs = record.split(';')
    
    for pair in pairs:
        if '=' in pair:
            tag, value = pair.split('=', 1)
            components[tag.strip()] = value.strip()
    
    return components

async def check_all_dns_records(domain: str) -> Dict[str, Any]:
    """
    Perform comprehensive DNS security check for a domain.
    
    Returns:
        Complete DNS analysis with scores and recommendations
    """
    # Run all checks concurrently
    mx_task = check_mx_records(domain)
    spf_task = check_spf_record(domain)
    dkim_task = check_dkim_records(domain)
    dmarc_task = check_dmarc_record(domain)
    
    mx_result, spf_result, dkim_result, dmarc_result = await asyncio.gather(
        mx_task, spf_task, dkim_task, dmarc_task
    )
    
    # Calculate total score
    total_score = (
        mx_result["score"] +
        spf_result["score"] +
        dkim_result["score"] +
        dmarc_result["score"]
    )
    
    # Generate grade
    grade = calculate_grade(total_score)
    
    # Collect all issues and recommendations
    all_issues = []
    all_recommendations = []
    
    for result in [mx_result, spf_result, dkim_result, dmarc_result]:
        all_issues.extend(result.get("issues", []))
    
    # Generate recommendations based on issues
    all_recommendations = generate_recommendations(mx_result, spf_result, dkim_result, dmarc_result)
    
    return {
        "mx": mx_result,
        "spf": spf_result,
        "dkim": dkim_result,
        "dmarc": dmarc_result,
        "total_score": total_score,
        "grade": grade,
        "issues": all_issues,
        "recommendations": all_recommendations
    }

def calculate_grade(score: int) -> str:
    """Calculate letter grade based on total score."""
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
    elif score >= 40:
        return "D"
    else:
        return "F"

def generate_recommendations(mx_result: Dict, spf_result: Dict, dkim_result: Dict, dmarc_result: Dict) -> List[str]:
    """Generate actionable recommendations based on DNS analysis results."""
    recommendations = []
    
    # MX recommendations
    if mx_result["status"] == "missing":
        recommendations.append("Configure MX records to enable email delivery for your domain")
    elif mx_result["status"] == "null_mx":
        recommendations.append("Remove null MX record if you want to receive emails")
    
    # SPF recommendations
    if spf_result["status"] == "missing":
        recommendations.append("Add SPF record to prevent email spoofing: 'v=spf1 -all' (adjust as needed)")
    elif "?all" in spf_result.get("mechanisms", []):
        recommendations.append("Strengthen SPF policy by changing '?all' to '-all' for better security")
    
    # DKIM recommendations
    if dkim_result["status"] == "missing":
        recommendations.append("Set up DKIM signing to improve email authentication and deliverability")
    elif dkim_result["status"] == "basic":
        recommendations.append("Add multiple DKIM selectors for redundancy and better security")
    
    # DMARC recommendations
    if dmarc_result["status"] == "missing":
        recommendations.append("Implement DMARC policy to enforce email authentication: start with 'p=none' for monitoring")
    elif dmarc_result.get("policy", {}).get("p") == "none":
        recommendations.append("Upgrade DMARC policy from 'none' to 'quarantine' or 'reject' for active protection")
    
    # General recommendations
    if len([r for r in [mx_result, spf_result, dkim_result, dmarc_result] if r["status"] in ["valid", "good"]]) < 3:
        recommendations.append("Complete email security setup with all four components: MX, SPF, DKIM, and DMARC")
    
    return recommendations
