# notifications.py
# SmartQueue – Gmail App Password + Render-Safe Fallback

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_ADDRESS, EMAIL_PASSWORD
import logging
import time


def send_email(to_email, subject, body):
    """
    This function tries to send an email through Gmail.
    If Render blocks SMTP (common on free tier), it falls back to LOG-ONLY mode.
    """

    # ----------- BUILD EMAIL -----------
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Small delay for Render’s cold start
        time.sleep(1)

        logging.info("📨 Attempting to send email via Gmail SMTP...")

        # ----------- CONNECT TO GMAIL SMTP -----------
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.ehlo()

        # ----------- LOGIN USING APP PASSWORD -----------
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        # ----------- SEND EMAIL -----------
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        server.quit()

        logging.info(f"✅ Email successfully SENT to {to_email}")
        return True

    except Exception as e:
        # ----------- FALLBACK: SAFE LOGGING -----------
        logging.error(f"❌ Email SEND FAILED: {e}")
        logging.info("\n📧 EMAIL LOGGED (NOT SENT — Render SMTP Blocked)")
        logging.info(f"To: {to_email}")
        logging.info(f"Subject: {subject}")
        logging.info(f"Body:\n{body}\n")

        return False
