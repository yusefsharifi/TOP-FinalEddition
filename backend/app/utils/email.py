from typing import Any, Dict
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, FileSystemLoader
from app.core.config import settings

# Configure FastMail
conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME=settings.PROJECT_NAME,
    MAIL_STARTTLS=settings.SMTP_TLS,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

# Initialize Jinja2 template environment
template_dir = Path(__file__).parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(template_dir)))

async def send_email(
    email_to: str,
    subject: str,
    template_name: str,
    template_data: Dict[str, Any]
) -> None:
    """
    Send an email using a template.
    
    Args:
        email_to: Recipient email address
        subject: Email subject
        template_name: Name of the template file (e.g., "reset_password.html")
        template_data: Dictionary of variables to pass to the template
    """
    template = env.get_template(template_name)
    html_content = template.render(**template_data)
    
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=html_content,
        subtype="html"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)

async def send_password_reset_email(
    email_to: str,
    username: str,
    reset_token: str
) -> None:
    """
    Send a password reset email to a user.
    
    Args:
        email_to: User's email address
        username: User's name or username
        reset_token: Password reset token
    """
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password Recovery"
    
    # Generate the password reset link
    reset_link = f"{settings.SERVER_HOST}/reset-password?token={reset_token}"
    
    template_data = {
        "username": username,
        "reset_link": reset_link,
        "expire_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
    }
    
    await send_email(
        email_to=email_to,
        subject=subject,
        template_name="reset_password.html",
        template_data=template_data
    ) 