import os
import logging
import requests

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_URL = "https://api.sendgrid.com/v3/mail/send"

logging.basicConfig(level=logging.INFO)

def send_email(to_email, subject, content):
    if not SENDGRID_API_KEY:
        logging.error("❌ SENDGRID_API_KEY is missing!")
        return False

    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "personalizations": [
            {"to": [{"email": to_email}],"subject": subject}
        ],
        "from": {"email": "no-reply@smartqueue.com"},
        "content": [{"type": "text/plain","value": content}]
    }

    try:
        response = requests.post(SENDGRID_URL, headers=headers, json=data)
        if response.status_code >= 200 and response.status_code < 300:
            logging.info(f"📧 Email sent to {to_email}")
            return True
        else:
            logging.error(f"❌ SendGrid Error: {response.text}")
            return False

    except Exception as e:
        logging.error(f"❌ ERROR sending email: {e}")
        return False
