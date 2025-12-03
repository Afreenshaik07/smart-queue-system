# config.py - FINAL VERSION

import os

ADMIN_ID = "admin"
ADMIN_PASSWORD = "admin"

# SendGrid (stored securely in Render Environment Variables)
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

# MUST MATCH YOUR VERIFIED SENDGRID SENDER EMAIL
SENDGRID_FROM_EMAIL = "d88368817@gmail.com"
