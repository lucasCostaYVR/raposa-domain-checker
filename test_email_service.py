#!/usr/bin/env python3
"""
Email Service Test Script
Use this to test your email service integration with the Redis queue.
"""

import os
import redis
import json
from datetime import datetime
import time

def create_test_domain_report():
    """Create a realistic test domain report message"""
    return {
        "to_email": "lucas.costa.1194@gmail.com",  # Replace with your test email
        "template": "domain_report",
        "data": {
            "domain": "test-domain.com",
            "score": 85,
            "grade": "A",
            "security_level": "Excellent",
            "analysis_results": {
            "id": 999,
            "domain": "test-domain.com",
            "mx_record": {
                "records": [{"preference": 10, "exchange": "mail.test-domain.com"}],
                "status": "valid",
                "issues": [],
                "score": 20,
                "explanation": {
                    "what_is": "MX (Mail Exchange) records tell other email servers where to deliver emails for your domain.",
                    "current_status": "✅ Your domain is properly configured to receive emails.",
                    "risk_if_misconfigured": "Emails sent to your domain will bounce back to senders."
                }
            },
            "spf_record": {
                "record": "v=spf1 include:_spf.google.com ~all",
                "status": "valid",
                "mechanisms": ["include:_spf.google.com", "~all"],
                "issues": [],
                "score": 25,
                "explanation": {
                    "what_is": "SPF prevents others from spoofing emails from your domain.",
                    "current_status": "✅ Your SPF record is properly configured.",
                    "risk_if_misconfigured": "Spammers could send emails pretending to be from your domain."
                }
            },
            "dkim_record": {
                "selectors": {
                    "default": {
                        "record": "v=DKIM1; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A...",
                        "selector": "default",
                        "status": "valid",
                        "score": 15
                    }
                },
                "status": "valid",
                "issues": [],
                "score": 15,
                "explanation": {
                    "what_is": "DKIM provides digital signatures to verify email authenticity.",
                    "current_status": "✅ DKIM is properly configured.",
                    "risk_if_misconfigured": "Emails may be marked as spam or rejected."
                }
            },
            "dmarc_record": {
                "record": "v=DMARC1; p=quarantine; rua=mailto:dmarc@test-domain.com",
                "status": "valid",
                "policy": {
                    "v": "DMARC1",
                    "p": "quarantine",
                    "rua": "mailto:dmarc@test-domain.com"
                },
                "issues": [],
                "score": 25,
                "explanation": {
                    "what_is": "DMARC tells email servers what to do with suspicious emails from your domain.",
                    "current_status": "✅ DMARC is properly configured.",
                    "risk_if_misconfigured": "Your domain could be used for phishing attacks."
                }
            },
            "score": 85,
            "grade": "A",
            "issues": [],
            "recommendations": [
                "Consider upgrading DMARC policy to 'reject' for maximum protection"
            ],
            "security_summary": {
                "security_level": "Excellent",
                "overall_message": "Your domain has strong email security configured.",
                "components_configured": "4/4 email security components properly configured",
                "grade_meaning": "Excellent email security. Your configuration is very strong.",
                "priority_actions": [],
                "protection_status": {
                    "spoofing_protection": "Protected",
                    "email_delivery": "Working",
                    "authentication": "Strong"
                }
            },
            "created_at": datetime.utcnow().isoformat() + "Z",
            "opt_in_marketing": False
        },
        "report_date": datetime.utcnow().strftime("%B %d, %Y"),
        "company_name": "Raposa"
    },
    "priority": "medium",
    "event_type": "domain_report.requested"
}

def publish_test_messages():
    """Publish test messages to Redis queue"""
    
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        print("❌ REDIS_URL environment variable not set")
        print("   Set it to: redis://default:password@host:port")
        return False
    
    try:
        # Connect to Redis
        redis_client = redis.from_url(redis_url)
        redis_client.ping()
        print("✅ Connected to Redis successfully")
        
        # Test: Domain report email
        print("\n📧 Publishing domain report test message...")
        domain_report = create_test_domain_report()
        # Queue the message using sorted set with priority scoring
        priority_score = {"high": 1000, "medium": 500, "low": 100}.get("medium", 500)
        timestamp_score = datetime.utcnow().timestamp() / 1000000
        final_score = priority_score + timestamp_score
        
        result = redis_client.zadd("raposa_email_queue", {json.dumps(domain_report): final_score})
        queue_length = redis_client.zcard("raposa_email_queue")
        print(f"✅ Domain report message queued (queue length: {queue_length}) with score {final_score}")
        
        print("\n🎉 Test message queued successfully!")
        print("   Check your email service logs to see if message was processed")
        print("   Check your email inbox for test email")
        print(f"   Current queue length: {queue_length}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to queue test message: {e}")
        return False

def monitor_queue():
    """Monitor the email queue for activity"""
    
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        print("❌ REDIS_URL environment variable not set")
        return
    
    try:
        redis_client = redis.from_url(redis_url)
        redis_client.ping()
        print("✅ Connected to Redis for monitoring")
        
        pubsub = redis_client.pubsub()
        pubsub.subscribe("email_queue")
        
        print("🔄 Monitoring email_queue channel...")
        print("   Press Ctrl+C to stop\n")
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    email_data = json.loads(message['data'].decode('utf-8'))
                    print(f"📧 Message received: {email_data['type']}")
                    print(f"   To: {email_data['to_email']}")
                    print(f"   Domain: {email_data.get('domain', 'N/A')}")
                    print(f"   Timestamp: {email_data['timestamp']}")
                    if email_data['type'] == 'domain_report':
                        analysis = email_data.get('analysis_results', {})
                        print(f"   Score: {analysis.get('score', 'N/A')}/100")
                        print(f"   Grade: {analysis.get('grade', 'N/A')}")
                    print("-" * 50)
                except Exception as e:
                    print(f"❌ Error parsing message: {e}")
                    
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")
    except Exception as e:
        print(f"❌ Monitoring error: {e}")

def check_redis_status():
    """Check Redis connection and queue status"""
    
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        print("❌ REDIS_URL environment variable not set")
        return
    
    try:
        redis_client = redis.from_url(redis_url)
        redis_client.ping()
        
        # Get Redis info
        info = redis_client.info()
        pubsub_info = redis_client.pubsub_numsub("email_queue")
        subscribers = pubsub_info[1] if len(pubsub_info) > 1 else 0
        
        print("📊 Redis Status:")
        print(f"   ✅ Connection: Working")
        print(f"   📦 Redis Version: {info.get('redis_version', 'unknown')}")
        print(f"   👥 Connected Clients: {info.get('connected_clients', 0)}")
        print(f"   📧 Email Queue Subscribers: {subscribers}")
        
        if subscribers == 0:
            print("   ⚠️  No email service subscribers detected")
            print("       Make sure your email service is running and subscribed")
        else:
            print("   ✅ Email service appears to be listening")
            
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Email Service Test Script")
        print("\nUsage:")
        print("  python test_email_service.py status    - Check Redis connection")
        print("  python test_email_service.py test      - Send test messages")
        print("  python test_email_service.py monitor   - Monitor queue activity")
        print("\nMake sure REDIS_URL environment variable is set!")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "status":
        check_redis_status()
    elif command == "test":
        publish_test_messages()
    elif command == "monitor":
        monitor_queue()
    else:
        print(f"❌ Unknown command: {command}")
        print("   Use: status, test, or monitor")
