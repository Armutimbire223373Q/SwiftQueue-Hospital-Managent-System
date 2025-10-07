import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from typing import List
from jinja2 import Environment, FileSystemLoader
import secrets
from datetime import datetime, timedelta

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "noreply@swiftqueue.com"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", ""),
    MAIL_FROM=EmailStr(os.getenv("MAIL_FROM", "noreply@swiftqueue.com")),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

# Initialize FastMail
fm = FastMail(conf)

# Jinja2 template environment
template_env = Environment(loader=FileSystemLoader("backend/app/templates"))

class EmailService:
    @staticmethod
    async def send_password_reset_email(email: EmailStr, reset_token: str, user_name: str):
        """Send password reset email to user."""
        try:
            # Generate reset link (adjust URL for your frontend)
            reset_link = f"http://localhost:5173/reset-password?token={reset_token}"

            # Load email template
            template = template_env.get_template("password_reset.html")

            # Render template with context
            html_content = template.render(
                user_name=user_name,
                reset_link=reset_link,
                expiry_hours=24
            )

            message = MessageSchema(
                subject="SwiftQueue Hospital - Password Reset Request",
                recipients=[email],
                body=html_content,
                subtype="html"
            )

            await fm.send_message(message)
            return True

        except Exception as e:
            print(f"Error sending password reset email: {str(e)}")
            return False

    @staticmethod
    async def send_welcome_email(email: EmailStr, user_name: str):
        """Send welcome email to new user."""
        try:
            template = template_env.get_template("welcome.html")

            html_content = template.render(
                user_name=user_name,
                login_url="http://localhost:5173/login"
            )

            message = MessageSchema(
                subject="Welcome to SwiftQueue Hospital Management System",
                recipients=[email],
                body=html_content,
                subtype="html"
            )

            await fm.send_message(message)
            return True

        except Exception as e:
            print(f"Error sending welcome email: {str(e)}")
            return False

    @staticmethod
    async def send_account_activation_email(email: EmailStr, user_name: str, activation_token: str):
        """Send account activation email."""
        try:
            activation_link = f"http://localhost:5173/activate?token={activation_token}"

            template = template_env.get_template("account_activation.html")

            html_content = template.render(
                user_name=user_name,
                activation_link=activation_link
            )

            message = MessageSchema(
                subject="SwiftQueue Hospital - Account Activation",
                recipients=[email],
                body=html_content,
                subtype="html"
            )

            await fm.send_message(message)
            return True

        except Exception as e:
            print(f"Error sending activation email: {str(e)}")
            return False

# Utility functions
def generate_reset_token() -> str:
    """Generate a secure random token for password reset."""
    return secrets.token_urlsafe(32)

def generate_activation_token() -> str:
    """Generate a secure random token for account activation."""
    return secrets.token_urlsafe(32)