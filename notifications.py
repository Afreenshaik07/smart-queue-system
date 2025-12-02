# notifications.py
# SAFE VERSION FOR RENDER (SMTP Disabled, Logs Only)

import logging

def send_email(to_email, subject, body):
    """
    Render Free Tier blocks Gmail/SMTP.
    So instead of sending real emails, we LOG them safely.

    Your app will continue working without errors.
    """

    logging.info("\n📧 EMAIL LOGGED (NOT SENT)")
    logging.info(f"To: {to_email}")
    logging.info(f"Subject: {subject}")
    logging.info(f"Body:\n{body}\n")

    # Always return True so the app thinks email was delivered
    return True
