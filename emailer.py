"""Send email using smtplib. Credentials come from .env, never hard-coded."""
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from utils import log

load_dotenv()


def send_email(subject, body, to=None):
    user = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    to = to or os.getenv("EMAIL_TO")
    if not (user and password and to):
        log.error("Email settings missing in .env")
        return False

    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = subject, user, to
    msg.set_content(body)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(user, password)
            server.send_message(msg)
        log.info("Email sent to %s", to)
        return True
    except smtplib.SMTPAuthenticationError:
        log.error("Login failed - use a Gmail App Password")
    except (smtplib.SMTPException, OSError) as e:
        log.error("Email failed: %s", e)
    return False
