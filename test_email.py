"""
Test script for the email service functionality.
"""

import os
import sys
import asyncio
import logging

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from email_service import get_email_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_email_service():
    """Test email service initialization and basic functionality."""
    
    try:
        logger.info("Testing email service initialization...")
        
        # Initialize email service (will use environment variables)
        email_service = get_email_service()
        logger.info("✅ Email service initialized successfully")
        
        # Test data
        test_domain = "github.com"
        test_email = "test@example.com"
        
        test_analysis_results = {
            "domain": test_domain,
            "score": 85,
            "grade": "A",
            "mx_record": {
                "status": "valid",
                "score": 20,
                "records": [{"preference": 1, "exchange": "aspmx.l.google.com"}]
            },
            "spf_record": {
                "status": "valid",
                "score": 25,
                "record": "v=spf1 include:_spf.google.com ~all"
            },
            "dkim_record": {
                "status": "valid",
                "score": 15,
                "selectors": {"google": {"status": "valid"}}
            },
            "dmarc_record": {
                "status": "valid",
                "score": 25,
                "record": "v=DMARC1; p=quarantine; rua=mailto:dmarc@github.com"
            },
            "issues": ["Minor SPF configuration could be improved"],
            "recommendations": [
                "Consider implementing DKIM for better email authentication",
                "Review DMARC policy for optimal security"
            ],
            "created_at": "2025-07-15T12:00:00Z"
        }
        
        # Uncomment the following lines to test actual email sending
        # NOTE: This will send real emails if Brevo credentials are configured
        
        # logger.info("Testing welcome email...")
        # welcome_result = await email_service.send_welcome_email(test_email, test_domain)
        # logger.info(f"Welcome email result: {welcome_result}")
        
        # logger.info("Testing domain report email...")
        # report_result = await email_service.send_domain_report(
        #     to_email=test_email,
        #     domain=test_domain,
        #     analysis_results=test_analysis_results,
        #     include_pdf=False  # Skip PDF for testing
        # )
        # logger.info(f"Domain report email result: {report_result}")
        
        logger.info("✅ Email service tests completed successfully!")
        logger.info("📧 Email sending tests are commented out to prevent sending test emails")
        logger.info("   Uncomment the email sending sections in test_email.py to test actual sending")
        
    except Exception as e:
        logger.error(f"❌ Email service test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_email_service())
    
    if success:
        print("\n🎉 Email service is ready for Phase 2.1!")
        print("📋 Next steps:")
        print("   1. Configure Brevo environment variables in production")
        print("   2. Test email sending with real credentials")
        print("   3. Deploy updated API with email functionality")
    else:
        print("\n❌ Email service tests failed. Please check configuration.")
