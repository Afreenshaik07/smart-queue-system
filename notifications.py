# notifications.py - FINAL WORKING SENDGRID VERSION

import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import SENDGRID_API_KEY, SENDGRID_FROM_EMAIL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EmailService")


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send email using SendGrid."""

    if not SENDGRID_API_KEY:
        logger.error("❌ SENDGRID_API_KEY missing! Check Render Environment Variables.")
        return False

    try:
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body,
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        logger.info(f"📧 Email sent successfully → {to_email} | STATUS: {response.status_code}")

        return 200 <= response.status_code < 300

    except Exception as e:
        logger.error(f"❌ ERROR sending email to {to_email}: {e}")
        return False


