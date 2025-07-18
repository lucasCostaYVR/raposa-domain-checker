"""
Email service module using SendGrid for sending domain reports with Jinja2 templates.
"""

import os
import logging
from typing import Dict, List, Optional
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment
import base64
from datetime import datetime
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

logger = logging.getLogger(__name__)

# Initialize Jinja2 environment
template_dir = Path(__file__).parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape(['html', 'xml'])
)



class SendGridEmailService:
    # ...existing code...
    """Email service using SendGrid API for sending domain security reports."""

    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_name = os.getenv("SENDGRID_FROM_NAME", "Raposa Domain Checker")
        self.from_email = os.getenv("SENDGRID_FROM_ADDRESS")

        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY environment variable is required")
        if not self.from_email:
            raise ValueError("SENDGRID_FROM_ADDRESS environment variable is required")

        self.sg = sendgrid.SendGridAPIClient(api_key=self.api_key)
        logger.info(f"SendGrid email service initialized with from: {self.from_name} <{self.from_email}>")

    async def send_domain_report(
        self,
        to_email: str,
        domain: str,
        analysis_results: Dict,
        include_pdf: bool = False
    ) -> bool:
        """Send a domain security report email using SendGrid with Jinja2 templates.
        
        Args:
            to_email: The recipient's email address
            domain: The domain that was analyzed
            analysis_results: Dictionary containing all analysis results
            include_pdf: Whether to include a PDF version (not implemented yet)
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Prepare template data
            template_data = self._prepare_template_data(domain, analysis_results)
            
            # Render templates
            html_template = jinja_env.get_template('domain_report.html')
            text_template = jinja_env.get_template('domain_report.txt')
            
            html_content = html_template.render(**template_data)
            text_content = text_template.render(**template_data)

            # Create the email message
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=f"Raposa Domain Security Report for {domain}",
                plain_text_content=Content("text/plain", text_content),
                html_content=Content("text/html", html_content)
            )

            # Attach PDF if requested
            if include_pdf:
                pdf_content = await self._generate_pdf_report(domain, analysis_results)
                if pdf_content:
                    attachment = Attachment()
                    attachment.file_content = pdf_content
                    attachment.file_type = "application/pdf"
                    attachment.file_name = f"domain_report_{domain}.pdf"
                    attachment.disposition = "attachment"
                    message.attachment = attachment

            # Send the email
            response = self.sg.send(message)
            
            if response.status_code in [200, 202]:
                logger.info(f"Domain report email sent successfully to {to_email} for {domain}")
                return True
            else:
                logger.error(f"Failed to send email. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending domain report email to {to_email} for {domain}: {e}")
            return False

        # Build HTML content (reuse your template)
        html_content = f"""
        <!DOCTYPE html>
        <html lang='en'>
        <head>
            <meta charset='utf-8'>
            <meta name='viewport' content='width=device-width, initial-scale=1.0'>
            <title>Raposa Domain Security Report - {domain}</title>
        </head>
        <body style='margin:0;padding:0;background:#000;font-family:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,\'Segoe UI\',Roboto,\'Helvetica Neue\',Arial,\'Noto Sans\',sans-serif;'>
            <table role='presentation' width='100%' cellpadding='0' cellspacing='0' border='0' style='background:#000;'>
                <tr>
                    <td align='center'>
                        <table width='600' cellpadding='0' cellspacing='0' border='0' style='background:#1e293b;border-radius:12px;box-shadow:0 10px 15px -3px rgba(0,0,0,0.1);margin:32px 0;'>
                            <tr>
                                <td style='background:linear-gradient(135deg,#3b82f6 0%,#8b5cf6 100%);padding:32px 20px 20px 20px;text-align:center;border-top-left-radius:12px;border-top-right-radius:12px;'>
                                    <div style='font-size:1.25rem;font-weight:700;color:#fff;letter-spacing:-0.025em;text-align:center;'>Raposa</div>
                                    <div style='font-size:0.75rem;color:#9ca3af;text-transform:uppercase;letter-spacing:0.1em;text-align:center;'>domain checker</div>
                                    <h2 style='margin:16px 0 0 0;text-decoration:none;color:#fff;font-size:1.5rem;font-weight:600;'>
                                        <span style='text-decoration:none;color:#fff;border-bottom:0;cursor:text;'>{domain}</span>
                                    </h2>
                                    <p style='margin:8px 0 0 0;color:#d1d5db;font-size:0.95rem;'>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                                </td>
                            </tr>
                            <tr>
                                <td style='padding:30px;'>
                                    <table width='100%' cellpadding='0' cellspacing='0' border='0'>
                                        <tr>
                                            <td style='background:{grade_color};color:#fff;padding:20px;text-align:center;border-radius:12px;'>
                                                <div style='font-size:48px;font-weight:bold;'>{score}/100</div>
                                                <div style='font-size:24px;margin-top:10px;'>Grade: {grade}</div>
                                            </td>
                                        </tr>
                                    </table>
                                    <h3 style='color:#fff;margin-top:32px;'>&#128202; Security Components Analysis</h3>
                                    <table width='100%' cellpadding='0' cellspacing='0' border='0'>
                                        <tr>
                                            <td style='background:#374151;border-left:4px solid #3b82f6;border-radius:12px;padding:15px;margin:15px 0;'>
                                                <div style='font-weight:bold;font-size:16px;color:#fff;'>{status_icon(mx_status)} MX Records (Mail Exchange)</div>
                                                <div style='margin-top:5px;color:#d1d5db;'>Status: {mx_status.title()} | Score: {results.get('mx_record', {}).get('score', 0)}/25</div>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style='background:#374151;border-left:4px solid #3b82f6;border-radius:12px;padding:15px;margin:15px 0;'>
                                                <div style='font-weight:bold;font-size:16px;color:#fff;'>{status_icon(spf_status)} SPF Record (Sender Policy Framework)</div>
                                                <div style='margin-top:5px;color:#d1d5db;'>Status: {spf_status.title()} | Score: {results.get('spf_record', {}).get('score', 0)}/25</div>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style='background:#374151;border-left:4px solid #3b82f6;border-radius:12px;padding:15px;margin:15px 0;'>
                                                <div style='font-weight:bold;font-size:16px;color:#fff;'>{status_icon(dkim_status)} DKIM Records (DomainKeys Identified Mail)</div>
                                                <div style='margin-top:5px;color:#d1d5db;'>Status: {dkim_status.title()} | Score: {results.get('dkim_record', {}).get('score', 0)}/25</div>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style='background:#374151;border-left:4px solid #3b82f6;border-radius:12px;padding:15px;margin:15px 0;'>
                                                <div style='font-weight:bold;font-size:16px;color:#fff;'>{status_icon(dmarc_status)} DMARC Record (Domain-based Message Authentication)</div>
                                                <div style='margin-top:5px;color:#d1d5db;'>Status: {dmarc_status.title()} | Score: {results.get('dmarc_record', {}).get('score', 0)}/25</div>
                                            </td>
                                        </tr>
                                    </table>
                                    <!-- Issues and Recommendations will be appended below -->
                                    <div style='margin-top:30px;padding-top:20px;border-top:1px solid #374151;'>
                                        <p style='font-size:1rem;color:#d1d5db;'><strong>Need help implementing these recommendations?</strong></p>
                                        <p style='font-size:0.95rem;color:#9ca3af;'>For technical support, reply to this email or visit our help center.</p>
                                    </div>
                                </td>
                            </tr>
                            <tr>
                                <td style='background:#1e293b;color:#9ca3af;padding:20px;text-align:center;font-size:12px;border-bottom-left-radius:12px;border-bottom-right-radius:12px;border-top:1px solid #374151;'>
                                    <p style='text-align:center;margin:0;'>This report was generated by <span style='color:#3b82f6;font-weight:600;'>Raposa Domain Checker</span></p>
                                    <p style='text-align:center;margin:0;'>Protecting your domain security, one check at a time.</p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        # Build plain text content
        text_content = self._generate_report_text(domain, analysis_results)

        # Prepare the email
        message = Mail(
            from_email=Email(self.from_email, self.from_name),
            to_emails=To(to_email),
            subject=f"Raposa Domain Security Report for {domain}",
            plain_text_content=Content("text/plain", text_content),
            html_content=Content("text/html", html_content)
        )

        # Optionally attach PDF (not implemented, placeholder)
        if include_pdf:
            pdf_b64 = await self._generate_pdf_report(domain, analysis_results)
            if pdf_b64:
                attachment = Attachment()
                attachment.file_content = pdf_b64
                attachment.file_type = "application/pdf"
                attachment.file_name = f"Raposa_Domain_Report_{domain}.pdf"
                attachment.disposition = "attachment"
                message.attachment = attachment

        # Send the email
        try:
            response = self.sg.send(message)
            logger.info(f"Domain report email sent to {to_email} for {domain}")
            logger.info(f"SendGrid response status: {response.status_code}")
            logger.info(f"SendGrid response body: {response.body}")
            logger.info(f"SendGrid response headers: {response.headers}")
            return response.status_code in [200, 202]
        except Exception as e:
            logger.error(f"Error sending domain report email to {to_email} for {domain}: {e}")
            return False

    def _prepare_template_data(self, domain: str, analysis_results: Dict) -> Dict:
        """Prepare data for template rendering."""
        def status_icon(status):
            icons = {"valid": "&#128994;", "warning": "&#128993;", "invalid": "&#128308;", "missing": "&#9898;"}
            return icons.get(status.lower(), "&#9898;")

        # Extract results data
        results = analysis_results.get("results", {})
        mx_record = results.get("mx_record", {})
        spf_record = results.get("spf_record", {})
        dkim_record = results.get("dkim_record", {})
        dmarc_record = results.get("dmarc_record", {})

        # Prepare security components data
        security_components = [
            {
                "name": "MX Records (Mail Exchange)",
                "status": mx_record.get("status", "unknown").title(),
                "score": mx_record.get("score", 0),
                "icon": status_icon(mx_record.get("status", "unknown"))
            },
            {
                "name": "SPF Record (Sender Policy Framework)",
                "status": spf_record.get("status", "unknown").title(),
                "score": spf_record.get("score", 0),
                "icon": status_icon(spf_record.get("status", "unknown"))
            },
            {
                "name": "DKIM Records (DomainKeys Identified Mail)",
                "status": dkim_record.get("status", "unknown").title(),
                "score": dkim_record.get("score", 0),
                "icon": status_icon(dkim_record.get("status", "unknown"))
            },
            {
                "name": "DMARC Record (Domain-based Message Authentication)",
                "status": dmarc_record.get("status", "unknown").title(),
                "score": dmarc_record.get("score", 0),
                "icon": status_icon(dmarc_record.get("status", "unknown"))
            }
        ]

        return {
            "domain": domain,
            "score": analysis_results.get("score", 0),
            "grade": analysis_results.get("grade", "F"),
            "grade_color": analysis_results.get("grade_color", "#374151"),
            "generated_date": datetime.now().strftime('%B %d, %Y at %I:%M %p'),
            "security_components": security_components,
            "issues": analysis_results.get("issues", []),
            "recommendations": analysis_results.get("recommendations", [])
        }

    async def _generate_pdf_report(self, domain: str, results: Dict) -> Optional[str]:
        """
        Generate PDF report and return base64 encoded content.

        TODO: Implement PDF generation using reportlab
        For now, return None to skip PDF attachment.
        """
        logger.info(f"PDF generation not yet implemented for domain {domain}")
        return None


    async def send_welcome_email(self, to_email: str, domain: str) -> bool:
        """Send a welcome email after first domain check using SendGrid and Jinja2 templates."""
        try:
            subject = f"Welcome to Raposa Domain Checker!"
            
            # Render welcome email template
            html_template = jinja_env.get_template('welcome_email.html')
            html_content = html_template.render(domain=domain)
            
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            response = self.sg.send(message)
            logger.info(f"Welcome email sent to {to_email}")
            logger.info(f"SendGrid response status: {response.status_code}")
            return response.status_code in [200, 202]
        except Exception as e:
            logger.error(f"Error sending welcome email to {to_email}: {e}")
            return False


# Global email service instance
email_service = None

def get_email_service() -> SendGridEmailService:
    """Get or create the global email service instance."""
    global email_service
    if email_service is None:
        email_service = SendGridEmailService()
    return email_service
