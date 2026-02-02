"""
Email service for sending verification codes
Supports: Gmail SMTP, SendGrid, and Mock Mode
"""

import smtplib
import secrets
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import requests

load_dotenv()

class EmailService:
    """Service for sending emails with verification codes"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL', '')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')
        
        # SendGrid configuration (alternative to SMTP)
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY', '')
        self.use_sendgrid = bool(self.sendgrid_api_key)
        
    @staticmethod
    def generate_verification_code(length: int = 6) -> str:
        """Generate a random verification code"""
        digits = string.digits
        return ''.join(secrets.choice(digits) for _ in range(length))
    
    def send_verification_email(self, recipient_email: str, user_name: str, code: str) -> bool:
        """Send verification code to user email"""
        
        # If SendGrid is configured, use it
        if self.use_sendgrid:
            return self._send_via_sendgrid(recipient_email, user_name, code, email_type="verification")
        
        # If no email credentials configured, use mock mode
        if not self.sender_email or not self.sender_password:
            print(f"\n MOCK EMAIL MODE - Verification Code for {recipient_email}: {code}")
            return True
        
        # Try SMTP (Gmail)
        return self._send_via_smtp(recipient_email, user_name, code, email_type="verification")
    
    def _send_via_sendgrid(self, recipient_email: str, user_name: str, code: str, email_type: str = "verification") -> bool:
        """Send email using SendGrid API"""
        try:
            url = "https://api.sendgrid.com/v3/mail/send"
            
            if email_type == "verification":
                subject = "Email Verification - Projura Agent"
                html_content = f"""\
                <html>
                    <body style="font-family: Arial, sans-serif;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #333;">Welcome to Projura Agent! 🎉</h2>
                            
                            <p>Hi <strong>{user_name}</strong>,</p>
                            
                            <p>Thank you for signing up! To verify your email address, please use the following code:</p>
                            
                            <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0;">
                                <h1 style="color: #2196F3; letter-spacing: 2px; margin: 0;">{code}</h1>
                            </div>
                            
                            <p>This code will expire in 10 minutes.</p>
                            
                            <p>If you didn't sign up for this account, please ignore this email.</p>
                            
                            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                            
                            <p style="font-size: 12px; color: #666;">
                                This is an automated email. Please do not reply to this message.
                            </p>
                        </div>
                    </body>
                </html>
                """
            else:
                subject = "Welcome to Projura Agent!"
                html_content = f"""\
                <html>
                    <body style="font-family: Arial, sans-serif;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #333;">Welcome to Projura Hub! 🚀</h2>
                            
                            <p>Hi <strong>{user_name}</strong>,</p>
                            
                            <p>Your email has been verified successfully! Your account is now active.</p>
                            
                            <p>You can now log in and start creating amazing projects with our AI-powered project ideas agent.</p>
                            
                            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                            
                            <p style="font-size: 12px; color: #666;">
                                Questions? Contact our support team.
                            </p>
                        </div>
                    </body>
                </html>
                """
            
            headers = {
                "Authorization": f"Bearer {self.sendgrid_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "personalizations": [{"to": [{"email": recipient_email}]}],
                "from": {"email": self.sender_email or "noreply@projura.com", "name": "Projura Agent"},
                "subject": subject,
                "content": [{"type": "text/html", "value": html_content}]
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 202:
                print(f" Email sent via SendGrid to {recipient_email}")
                return True
            else:
                print(f"❌ SendGrid error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to send email via SendGrid: {str(e)}")
            return False
    
    def _send_via_smtp(self, recipient_email: str, user_name: str, code: str, email_type: str = "verification") -> bool:
        """Send email using SMTP (Gmail)"""
        try:
            if email_type == "verification":
                subject = "Email Verification - Projura Agent"
                html = f"""\
                <html>
                    <body style="font-family: Arial, sans-serif;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #333;">Welcome to Projura Agent! 🎉</h2>
                            
                            <p>Hi <strong>{user_name}</strong>,</p>
                            
                            <p>Thank you for signing up! To verify your email address, please use the following code:</p>
                            
                            <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0;">
                                <h1 style="color: #2196F3; letter-spacing: 2px; margin: 0;">{code}</h1>
                            </div>
                            
                            <p>This code will expire in 10 minutes.</p>
                            
                            <p>If you didn't sign up for this account, please ignore this email.</p>
                            
                            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                            
                            <p style="font-size: 12px; color: #666;">
                                This is an automated email. Please do not reply to this message.
                            </p>
                        </div>
                    </body>
                </html>
                """
            else:
                subject = "Welcome to Projura Agent!"
                html = f"""\
                <html>
                    <body style="font-family: Arial, sans-serif;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #333;">Welcome Aboard! 🚀</h2>
                            
                            <p>Hi <strong>{user_name}</strong>,</p>
                            
                            <p>Your email has been verified successfully! Your account is now active.</p>
                            
                            <p>You can now log in and start creating amazing projects.</p>
                            
                            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                            
                            <p style="font-size: 12px; color: #666;">
                                This is an automated email. Please do not reply to this message.
                            </p>
                        </div>
                    </body>
                </html>
                """
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Attach HTML to message
            part = MIMEText(html, "html")
            message.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(
                    self.sender_email,
                    recipient_email,
                    message.as_string()
                )
            
            print(f"✅ Email sent via SMTP to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email via SMTP: {str(e)}")
            return False
    
    def send_welcome_email(self, recipient_email: str, user_name: str) -> bool:
        """Send welcome email after successful verification"""
        
        # If SendGrid is configured, use it
        if self.use_sendgrid:
            return self._send_via_sendgrid(recipient_email, user_name, "", email_type="welcome")
        
        # If no email credentials configured, use mock mode
        if not self.sender_email or not self.sender_password:
            print(f"\n📧 MOCK EMAIL MODE - Welcome email for {recipient_email}")
            return True
        
        return self._send_via_smtp(recipient_email, user_name, "", email_type="welcome")
    
    @staticmethod
    def get_expiration_time(minutes: int = 20) -> str:
        """Get expiration timestamp"""
        return (datetime.utcnow() + timedelta(minutes=minutes)).isoformat()


# Initialize email service
email_service = EmailService()
