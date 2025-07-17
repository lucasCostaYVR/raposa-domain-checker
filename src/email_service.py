"""
Email service module using Brevo (formerly Sendinblue) for sending domain reports.
"""

import os
import logging
from typing import Dict, List, Optional
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class BrevoEmailService:
    """Email service using Brevo API for sending domain security reports."""

    def __init__(self):
        """Initialize Brevo email service with API configuration."""
        self.api_key = os.getenv("BREVO_API_KEY")
        self.from_name = os.getenv("BREVO_FROM_NAME", "Raposa Domain Checker")
        self.from_email = os.getenv("BREVO_FROM_ADDRESS")

        if not self.api_key:
            raise ValueError("BREVO_API_KEY environment variable is required")
        if not self.from_email:
            raise ValueError("BREVO_FROM_ADDRESS environment variable is required")

        # Configure Brevo API
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = self.api_key

        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        logger.info(f"Brevo email service initialized with from: {self.from_name} <{self.from_email}>")

    async def send_domain_report(
        self,
        to_email: str,
        domain: str,
        analysis_results: Dict,
        include_pdf: bool = True
    ) -> bool:
        """
        Send a comprehensive domain security report email.

        Args:
            to_email: Recipient email address
            domain: Domain that was analyzed
            analysis_results: Complete analysis results from check_domain
            include_pdf: Whether to include PDF report attachment

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Prepare email content
            subject = f"Your Domain Security Report for {domain}"

            # Generate HTML content
            html_content = self._generate_report_html(domain, analysis_results)

            # Create email
            email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email}],
                sender={"name": self.from_name, "email": self.from_email},
                subject=subject,
                html_content=html_content,
                text_content=self._generate_report_text(domain, analysis_results)
            )

            # Add PDF attachment if requested
            if include_pdf:
                pdf_content = await self._generate_pdf_report(domain, analysis_results)
                if pdf_content:
                    email.attachment = [{
                        "content": pdf_content,
                        "name": f"{domain}_security_report.pdf"
                    }]

            # Send email
            api_response = self.api_instance.send_transac_email(email)
            logger.info(f"Domain report email sent successfully to {to_email} for domain {domain}")
            logger.debug(f"Brevo response: {api_response}")

            return True

        except ApiException as e:
            logger.error(f"Brevo API error sending email to {to_email}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {e}")
            return False

    def _generate_report_html(self, domain: str, results: Dict) -> str:
        """Generate HTML content for the domain report email."""

        # Extract key metrics
        score = results.get("score", 0)
        grade = results.get("grade", "F")
        issues = results.get("issues", [])
        recommendations = results.get("recommendations", [])

        # Status colors
        grade_color = {
            "A+": "#28a745", "A": "#28a745", "A-": "#28a745",
            "B+": "#17a2b8", "B": "#17a2b8", "B-": "#17a2b8",
            "C+": "#ffc107", "C": "#ffc107", "C-": "#ffc107",
            "D+": "#fd7e14", "D": "#fd7e14", "D-": "#fd7e14",
            "F": "#dc3545"
        }.get(grade, "#6c757d")

        # Generate component status
        mx_status = results.get("mx_record", {}).get("status", "unknown")
        spf_status = results.get("spf_record", {}).get("status", "unknown")
        dkim_status = results.get("dkim_record", {}).get("status", "unknown")
        dmarc_status = results.get("dmarc_record", {}).get("status", "unknown")

        def status_icon(status):
            if status == "valid":
                return "✅"
            elif status == "warning":
                return "⚠️"
            else:
                return "❌"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Domain Security Report - {domain}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #f9f9f9; }}
                .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background: white; }}
                .score-card {{ background: {grade_color}; color: white; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px; }}
                .score-number {{ font-size: 48px; font-weight: bold; }}
                .grade {{ font-size: 24px; margin-top: 10px; }}
                .component {{ margin: 15px 0; padding: 15px; border-left: 4px solid #007bff; background: #f8f9fa; }}
                .component-title {{ font-weight: bold; font-size: 16px; }}
                .component-status {{ margin-top: 5px; }}
                .issues {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 20px 0; border-radius: 4px; }}
                .recommendations {{ background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; margin: 20px 0; border-radius: 4px; }}
                .footer {{ background: #6c757d; color: white; padding: 20px; text-align: center; font-size: 12px; }}
                ul {{ padding-left: 20px; }}
                li {{ margin: 8px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ Domain Security Report</h1>
                    <h2>{domain}</h2>
                    <p>Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
                </div>

                <div class="content">
                    <div class="score-card">
                        <div class="score-number">{score}/100</div>
                        <div class="grade">Grade: {grade}</div>
                    </div>

                    <h3>📊 Security Components Analysis</h3>

                    <div class="component">
                        <div class="component-title">{status_icon(mx_status)} MX Records (Mail Exchange)</div>
                        <div class="component-status">Status: {mx_status.title()} | Score: {results.get("mx_record", {}).get("score", 0)}/25</div>
                    </div>

                    <div class="component">
                        <div class="component-title">{status_icon(spf_status)} SPF Record (Sender Policy Framework)</div>
                        <div class="component-status">Status: {spf_status.title()} | Score: {results.get("spf_record", {}).get("score", 0)}/25</div>
                    </div>

                    <div class="component">
                        <div class="component-title">{status_icon(dkim_status)} DKIM Records (DomainKeys Identified Mail)</div>
                        <div class="component-status">Status: {dkim_status.title()} | Score: {results.get("dkim_record", {}).get("score", 0)}/25</div>
                    </div>

                    <div class="component">
                        <div class="component-title">{status_icon(dmarc_status)} DMARC Record (Domain-based Message Authentication)</div>
                        <div class="component-status">Status: {dmarc_status.title()} | Score: {results.get("dmarc_record", {}).get("score", 0)}/25</div>
                    </div>
        """

        # Add issues section if there are any
        if issues:
            html_content += f"""
                    <div class="issues">
                        <h4>⚠️ Issues Found</h4>
                        <ul>
                            {"".join(f"<li>{issue}</li>" for issue in issues)}
                        </ul>
                    </div>
            """

        # Add recommendations section
        if recommendations:
            html_content += f"""
                    <div class="recommendations">
                        <h4>💡 Recommendations</h4>
                        <ul>
                            {"".join(f"<li>{rec}</li>" for rec in recommendations)}
                        </ul>
                    </div>
            """

        html_content += """
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                        <p><strong>Need help implementing these recommendations?</strong></p>
                        <p>Our detailed PDF report (attached) includes step-by-step instructions for improving your domain security.</p>
                        <p>For technical support, reply to this email or visit our help center.</p>
                    </div>
                </div>

                <div class="footer">
                    <p>This report was generated by Raposa Domain Checker</p>
                    <p>Protecting your domain security, one check at a time.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html_content

    def _generate_report_text(self, domain: str, results: Dict) -> str:
        """Generate plain text version of the domain report."""

        score = results.get("score", 0)
        grade = results.get("grade", "F")
        issues = results.get("issues", [])
        recommendations = results.get("recommendations", [])

        text_content = f"""
Domain Security Report for {domain}
Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}

OVERALL SECURITY SCORE: {score}/100 (Grade: {grade})

COMPONENT ANALYSIS:
• MX Records: {results.get("mx_record", {}).get("status", "unknown").title()}
• SPF Record: {results.get("spf_record", {}).get("status", "unknown").title()}
• DKIM Records: {results.get("dkim_record", {}).get("status", "unknown").title()}
• DMARC Record: {results.get("dmarc_record", {}).get("status", "unknown").title()}
        """

        if issues:
            text_content += f"\n\nISSUES FOUND:\n"
            for issue in issues:
                text_content += f"• {issue}\n"

        if recommendations:
            text_content += f"\n\nRECOMMENDATIONS:\n"
            for rec in recommendations:
                text_content += f"• {rec}\n"

        text_content += """

For detailed implementation instructions, please see the attached PDF report.

Need help? Reply to this email for technical support.

---
Raposa Domain Checker
Protecting your domain security, one check at a time.
        """

        return text_content

    async def _generate_pdf_report(self, domain: str, results: Dict) -> Optional[str]:
        """
        Generate PDF report and return base64 encoded content.

        TODO: Implement PDF generation using reportlab
        For now, return None to skip PDF attachment.
        """
        # This will be implemented in the next step
        logger.info(f"PDF generation not yet implemented for domain {domain}")
        return None

    async def send_welcome_email(self, to_email: str, domain: str) -> bool:
        """Send a welcome email after first domain check."""
        try:
            subject = f"Welcome to Raposa Domain Checker!"

            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>Welcome to Raposa Domain Checker! 🎉</h2>

                    <p>Thank you for checking the security of <strong>{domain}</strong>!</p>

                    <p>You'll receive a detailed security report shortly with:</p>
                    <ul>
                        <li>📊 Complete DNS analysis</li>
                        <li>🛡️ Security score and grade</li>
                        <li>💡 Actionable recommendations</li>
                        <li>📋 Step-by-step implementation guides</li>
                    </ul>

                    <p>Questions? Just reply to this email - we're here to help!</p>

                    <p>Best regards,<br>The Raposa Team</p>
                </div>
            </body>
            </html>
            """

            email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email}],
                sender={"name": self.from_name, "email": self.from_email},
                subject=subject,
                html_content=html_content
            )

            self.api_instance.send_transac_email(email)
            logger.info(f"Welcome email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Error sending welcome email to {to_email}: {e}")
            return False


# Global email service instance
email_service = None

def get_email_service() -> BrevoEmailService:
    """Get or create the global email service instance."""
    global email_service
    if email_service is None:
        email_service = BrevoEmailService()
    return email_service
