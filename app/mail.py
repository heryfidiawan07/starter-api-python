import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .config import settings


def _send(to: str, subject: str, html_body: str) -> None:
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{settings.mail_from_name} <{settings.mail_from}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.mail_host, settings.mail_port) as server:
            server.ehlo()
            server.starttls()
            if settings.mail_user:
                server.login(settings.mail_user, settings.mail_pass)
            server.sendmail(settings.mail_from, to, msg.as_string())
    except Exception as e:
        print(f"Failed to send email to {to}: {e}")


def send_verification_email(to: str, name: str, token: str) -> None:
    link = f"{settings.app_url}/api/v1/auth/verify-email?token={token}"
    body = (
        f"<p>Hi {name},</p>"
        f"<p>Click the link below to verify your email address:</p>"
        f"<p><a href='{link}'>{link}</a></p>"
        f"<p>This link expires in 24 hours.</p>"
    )
    _send(to, "Verify Your Email", body)


def send_password_reset_email(to: str, name: str, token: str) -> None:
    link = f"{settings.app_url}/reset-password?token={token}"
    body = (
        f"<p>Hi {name},</p>"
        f"<p>Click the link below to reset your password:</p>"
        f"<p><a href='{link}'>{link}</a></p>"
        f"<p>This link expires in 1 hour.</p>"
        f"<p>If you did not request this, ignore this email.</p>"
    )
    _send(to, "Reset Your Password", body)
