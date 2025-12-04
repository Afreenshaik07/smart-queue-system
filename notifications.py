import os
import requests
import json
import logging

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

def send_email(to_email, subject, message):
    try:
        url = "https://api.sendgrid.com/v3/mail/send"

        headers = {
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "personalizations": [{
                "to": [{"email": to_email}]
            }],
            "from": {"email": "queue-system@example.com"},
            "subject": subject,
            "content": [{
                "type": "text/plain",
                "value": message
            }]
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code >= 200 and response.status_code < 300:
            logging.info("✅ Email sent successfully")
        else:
            logging.error(f"❌ Email failed: {response.status_code} - {response.text}")

    except Exception as e:
        logging.error(f"❌ ERROR sending email: {e}")
