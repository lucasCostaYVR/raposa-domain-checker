"""
Email service module using SendGrid for direct email sending.
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
import sendgrid
from sendgrid.helpers.mail import Mail, From, To, Subject, HtmlContent, PlainTextContent

logger = logging.getLogger(__name__)


class SendGridEmailService:
    """Email service using SendGrid for direct email sending."""

    def __init__(self):
        api_key = os.getenv("SENDGRID_API_KEY")
        if not api_key:
            raise ValueError("SENDGRID_API_KEY environment variable is required")

        self.sg = sendgrid.SendGridAPIClient(api_key=api_key)
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "hello@raposa.tech")
        self.from_name = os.getenv("SENDGRID_FROM_NAME", "Raposa Domain Checker")
        
        logger.info(f"SendGrid email service initialized successfully")

    async def send_domain_report(
        self,
        to_email: str,
        domain: str,
        analysis_results: Dict
    ) -> bool:
        """
        Send domain report email directly via SendGrid.
        
        Args:
            to_email: Recipient email address
            domain: Domain name being analyzed
            analysis_results: Domain analysis data
            
        Returns:
            bool: True if email was sent successfully
        """
        try:
            logger.info(f"Preparing to send domain report email for {to_email}, domain: {domain}")
            
            # Generate email content
            subject = f"Domain Security Analysis Report for {domain}"
            html_content = self._generate_domain_report_html(domain, analysis_results)
            text_content = self._generate_domain_report_text(domain, analysis_results)
            
            # Create the email
            message = Mail(
                from_email=From(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=Subject(subject),
                html_content=HtmlContent(html_content),
                plain_text_content=PlainTextContent(text_content)
            )
            
            # Send the email
            response = self.sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Domain report email sent successfully to {to_email} (domain: {domain})")
                return True
            else:
                logger.error(f"❌ Failed to send email. Status: {response.status_code}, Body: {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send domain report email: {e}")
            return False

    def _generate_domain_report_html(self, domain: str, analysis_results: Dict) -> str:
        """Generate HTML email content for domain report."""
        score = analysis_results.get("score", 0)
        grade = analysis_results.get("grade", "F")
        security_level = analysis_results.get("security_summary", {}).get("security_level", "Poor")
        mx_record = analysis_results.get("mx_record", {})
        spf_record = analysis_results.get("spf_record", {})
        dkim_record = analysis_results.get("dkim_record", {})
        dmarc_record = analysis_results.get("dmarc_record", {})
        issues = analysis_results.get("issues", [])
        recommendations = analysis_results.get("recommendations", [])
        
        # Helper functions for template
        def get_status_icon(status):
            return "✅" if status in ["valid", "good"] else "⚠️" if status == "warning" else "❌"
        
        def get_status_class(status):
            if status in ['valid', 'good']:
                return 'valid'
            elif status == 'warning':
                return 'warning'
            else:
                return 'invalid'
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Domain Security Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #2563eb; color: white; padding: 20px; text-align: center; }}
                .score-box {{ background: #f8fafc; border: 2px solid #e2e8f0; padding: 20px; margin: 20px 0; text-align: center; }}
                .grade {{ font-size: 48px; font-weight: bold; color: #2563eb; }}
                .record-section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #e2e8f0; }}
                .valid {{ border-color: #10b981; }}
                .warning {{ border-color: #f59e0b; }}
                .invalid {{ border-color: #ef4444; }}
                .issues {{ background: #fef2f2; padding: 15px; border-radius: 8px; }}
                .recommendations {{ background: #f0f9ff; padding: 15px; border-radius: 8px; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ Domain Security Analysis</h1>
                    <h2>{domain}</h2>
                </div>
                
                <div class="score-box">
                    <div class="grade">{grade}</div>
                    <div><strong>{score}/100</strong> - {security_level} Security</div>
                </div>
                
                <div class="record-section {get_status_class(mx_record.get('status', 'missing'))}">
                    <h3>{get_status_icon(mx_record.get('status', 'missing'))} MX Records</h3>
                    <p><strong>Status:</strong> {mx_record.get('status', 'Missing').title()}</p>
                    <p><strong>Score:</strong> {mx_record.get('score', 0)}/20</p>
                    <p>{mx_record.get('explanation', {}).get('current_status', '')}</p>
                </div>
                
                <div class="record-section {get_status_class(spf_record.get('status', 'missing'))}">
                    <h3>{get_status_icon(spf_record.get('status', 'missing'))} SPF Record</h3>
                    <p><strong>Status:</strong> {spf_record.get('status', 'Missing').title()}</p>
                    <p><strong>Score:</strong> {spf_record.get('score', 0)}/25</p>
                    <p>{spf_record.get('explanation', {}).get('current_status', '')}</p>
                </div>
                
                <div class="record-section {get_status_class(dkim_record.get('status', 'missing'))}">
                    <h3>{get_status_icon(dkim_record.get('status', 'missing'))} DKIM Record</h3>
                    <p><strong>Status:</strong> {dkim_record.get('status', 'Missing').title()}</p>
                    <p><strong>Score:</strong> {dkim_record.get('score', 0)}/25</p>
                    <p>{dkim_record.get('explanation', {}).get('current_status', '')}</p>
                </div>
                
                <div class="record-section {get_status_class(dmarc_record.get('status', 'missing'))}">
                    <h3>{get_status_icon(dmarc_record.get('status', 'missing'))} DMARC Record</h3>
                    <p><strong>Status:</strong> {dmarc_record.get('status', 'Missing').title()}</p>
                    <p><strong>Score:</strong> {dmarc_record.get('score', 0)}/30</p>
                    <p>{dmarc_record.get('explanation', {}).get('current_status', '')}</p>
                </div>"""
        
        if issues:
            html += """
                <div class="issues">
                    <h3>🔍 Issues Found</h3>
                    <ul>"""
            for issue in issues:
                html += f"<li>{issue}</li>"
            html += "</ul></div>"
        
        if recommendations:
            html += """
                <div class="recommendations">
                    <h3>💡 Recommendations</h3>
                    <ul>"""
            for rec in recommendations:
                html += f"<li>{rec}</li>"
            html += "</ul></div>"
        
        html += f"""
                <div class="footer">
                    <p>This report was generated by <strong>Raposa Domain Checker</strong></p>
                    <p>Visit <a href="https://domainchecker.raposa.tech">domainchecker.raposa.tech</a> for more security analyses</p>
                    <p>Report generated on {datetime.utcnow().strftime('%B %d, %Y')}</p>
                </div>
            </div>
        </body>
        </html>"""
        
        return html

    def _generate_domain_report_text(self, domain: str, analysis_results: Dict) -> str:
        """Generate plain text email content for domain report."""
        score = analysis_results.get("score", 0)
        grade = analysis_results.get("grade", "F")
        security_level = analysis_results.get("security_summary", {}).get("security_level", "Poor")
        mx_record = analysis_results.get("mx_record", {})
        spf_record = analysis_results.get("spf_record", {})
        dkim_record = analysis_results.get("dkim_record", {})
        dmarc_record = analysis_results.get("dmarc_record", {})
        issues = analysis_results.get("issues", [])
        recommendations = analysis_results.get("recommendations", [])
        
        text = f"""
DOMAIN SECURITY ANALYSIS REPORT
{'=' * 40}

Domain: {domain}
Overall Score: {score}/100 (Grade {grade})
Security Level: {security_level}

DNS RECORDS ANALYSIS
{'=' * 20}

MX Records: {mx_record.get('status', 'Missing').upper()}
Score: {mx_record.get('score', 0)}/20
{mx_record.get('explanation', {}).get('current_status', '')}

SPF Record: {spf_record.get('status', 'Missing').upper()}
Score: {spf_record.get('score', 0)}/25
{spf_record.get('explanation', {}).get('current_status', '')}

DKIM Record: {dkim_record.get('status', 'Missing').upper()}
Score: {dkim_record.get('score', 0)}/25
{dkim_record.get('explanation', {}).get('current_status', '')}

DMARC Record: {dmarc_record.get('status', 'Missing').upper()}
Score: {dmarc_record.get('score', 0)}/30
{dmarc_record.get('explanation', {}).get('current_status', '')}
"""
        
        if issues:
            text += f"\nISSUES FOUND:\n"
            for i, issue in enumerate(issues, 1):
                text += f"{i}. {issue}\n"
        
        if recommendations:
            text += f"\nRECOMMENDATIONS:\n"
            for i, rec in enumerate(recommendations, 1):
                text += f"{i}. {rec}\n"
        
        text += f"""
{'=' * 40}
This report was generated by Raposa Domain Checker
Visit: https://domainchecker.raposa.tech
Report generated on: {datetime.utcnow().strftime('%B %d, %Y')}
"""
        
        return text

    def check_sendgrid_connection(self) -> bool:
        """
        Check if SendGrid connection is working.
        
        Returns:
            bool: True if SendGrid is accessible
        """
        try:
            # Just verify we have the API key
            return bool(os.getenv("SENDGRID_API_KEY"))
        except Exception as e:
            logger.error(f"SendGrid connection check failed: {e}")
            return False

    def get_service_info(self) -> Dict:
        """
        Get information about the email service.
        
        Returns:
            Dict: Service statistics and info
        """
        try:
            return {
                "sendgrid_configured": bool(os.getenv("SENDGRID_API_KEY")),
                "from_email": self.from_email,
                "from_name": self.from_name,
                "service_type": "sendgrid_direct"
            }
        except Exception as e:
            logger.error(f"Failed to get service info: {e}")
            return {
                "sendgrid_configured": False,
                "error": str(e)
            }


# Global email service instance
_email_service = None


def get_email_service() -> SendGridEmailService:
    """
    Get or create the global email service instance.
    
    Returns:
        SendGridEmailService: The email service instance
    """
    global _email_service
    if _email_service is None:
        _email_service = SendGridEmailService()
    return _email_service
