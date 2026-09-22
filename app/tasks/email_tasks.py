import os
import smtplib
from email.message import EmailMessage

from app.celery_app import celery


@celery.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True
)
def send_email_task(self, to_email, subject, body):

    smtp_server = os.getenv("MAIL_SERVER")
    smtp_port = int(os.getenv("MAIL_PORT", 587))
    username = os.getenv("MAIL_USERNAME")
    password = os.getenv("MAIL_PASSWORD")
    mail_from = os.getenv("MAIL_FROM", username)

    if not username or not password:
        raise ValueError("Email configuration is missing")

    message = EmailMessage()

    message["From"] = mail_from
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(body)

    with smtplib.SMTP(smtp_server, smtp_port) as server:

        server.starttls()

        server.login(username, password)

        server.send_message(message)

    print("================================")
    print("REAL EMAIL SENT")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print("================================")

    return "Email sent successfully"