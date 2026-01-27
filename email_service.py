"""
Email service for sending verification codes
"""

import smtplib
import secrets
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    """Service for sending emails with verification codes"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL', '')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')
        
    @staticmethod
    def generate_verification_code(length: int = 6) -> str:
        """Generate a random verification code"""
        digits = string.digits
        return ''.join(secrets.choice(digits) for _ in range(length))
    
    def send_verification_email(self, recipient_email: str, user_name: str, code: str) -> bool:
        """Send verification code to user email"""
        
        # If no email credentials configured, use mock mode
        if not self.sender_email or not self.sender_password:
            print(f"\n📧 MOCK EMAIL MODE - Verification Code for {recipient_email}: {code}")
            return True
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Email Verification - Projura Agent"
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Create HTML email body
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
            
            print(f"✅ Verification email sent to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")
            return False
    
    def send_welcome_email(self, recipient_email: str, user_name: str) -> bool:
        """Send welcome email after successful verification"""
        
        if not self.sender_email or not self.sender_password:
            print(f"\n📧 MOCK EMAIL MODE - Welcome email for {recipient_email}")
            return True
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = "Welcome to Projura Agent!"
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            html = f"""\
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #333;">Welcome Aboard! 🚀</h2>
                        
                        <p>Hi <strong>{user_name}</strong>,</p>
                        
                        <p>Your email has been verified successfully! Your account is now active.</p>
                        
                        <p>You can now log in and start creating amazing projects with our AI-powered project ideas agent.</p>
                        
                        <p style="margin-top: 20px;">
                            <a href="http://localhost:5000/login" style="background-color: #2196F3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                Go to Login
                            </a>
                        </p>
                        
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                        
                        <p style="font-size: 12px; color: #666;">
                            Questions? Contact our support team.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            part = MIMEText(html, "html")
            message.attach(part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(
                    self.sender_email,
                    recipient_email,
                    message.as_string()
                )
            
            print(f"✅ Welcome email sent to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send welcome email: {str(e)}")
            return False
    
    @staticmethod
    def get_expiration_time(minutes: int = 20) -> str:
        """Get expiration timestamp"""
        return (datetime.utcnow() + timedelta(minutes=minutes)).isoformat()


# Initialize email service
email_service = EmailService()
