import os
import requests
import logging

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")

def send_email(to_email, subject, content):
    if not SENDGRID_API_KEY:
        logging.error("❌ SendGrid key missing!")
        return False

    url = "https://api.sendgrid.com/v3/mail/send"

    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "personalizations": [
            {"to": [{"email": to_email}]}
        ],
        "from": {"email": "smartqueue@system.com"},
        "subject": subject,
        "content": [{"type": "text/plain", "value": content}]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 202:
            logging.info(f"📨 Email sent → {to_email}")
            return True
        else:
            logging.error(f"❌ SendGrid Error {response.status_code}: {response.text}")
            return False

    except Exception as e:
        logging.error(f"❌ ERROR sending email: {e}")
        return False
