import requests
from config import SENDGRID_API_KEY

def send_email(to_email, subject, body):
    url = "https://api.sendgrid.com/v3/mail/send"

    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "personalizations": [{
            "to": [{"email": to_email}],
            "subject": subject
        }],
        "from": {"email": "d88368817@gmail.com"},   # your verified sender
        "content": [{
            "type": "text/plain",
            "value": body
        }]
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 202:
        print("✅ Email sent successfully!")
        return True
    else:
        print("❌ Email failed:", response.text)
        return False
