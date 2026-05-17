import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tasks.celery_app import celery_app


SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER)


@celery_app.task(
    name="tasks.email_tasks.send_alert_email",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
)
def send_alert_email(self, to: str, subject: str, body: str):
    """
    Sends an alert email via SMTP.
    Retries up to 3 times if it fails.

    Args:
        to:      recipient email address
        subject: email subject line
        body:    plain text email body
    """
    print(f"[email] Sending to {to}: {subject}")

    try:
        msg = MIMEMultipart("alternative")
        msg["From"]    = EMAIL_FROM
        msg["To"]      = to
        msg["Subject"] = subject

        # plain text version
        msg.attach(MIMEText(body, "plain"))

        # html version — wraps the body in a simple styled template
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; border-left: 4px solid #e74c3c; padding: 16px; border-radius: 4px;">
              <h2 style="color: #e74c3c; margin: 0 0 12px 0;">⚠️ SmartClass Alert</h2>
              <p style="color: #333; margin: 0; white-space: pre-line;">{body}</p>
            </div>
            <p style="color: #999; font-size: 12px; margin-top: 16px;">
              This is an automated alert from SmartClass.
            </p>
          </body>
        </html>
        """
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, to, msg.as_string())

        print(f"[email] Sent successfully to {to}")
        return {"status": "sent", "to": to}

    except Exception as exc:
        print(f"[email] Failed to send to {to}: {exc}")
        raise self.retry(exc=exc)