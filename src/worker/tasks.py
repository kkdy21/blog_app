import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

from src.worker.celery_app import celery_app


@celery_app.task(name="send_email")
def send_email(to_email: str, subject: str, html_body: str) -> dict:
    smtp_host = os.getenv("SMTP_HOST", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", "25"))
    smtp_user = os.getenv("SMTP_USER") or None
    smtp_pass = os.getenv("SMTP_PASS") or None
    smtp_tls = os.getenv("SMTP_TLS", "false").lower() == "true"
    smtp_from = os.getenv("SMTP_FROM", "no-reply@example.com")

    msg = MIMEText(html_body, "html", _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = smtp_from
    msg["To"] = to_email
    msg["Date"] = formatdate(localtime=True)

    with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as smtp:
        if smtp_tls:
            smtp.starttls()
        if smtp_user and smtp_pass:
            try:
                smtp.login(smtp_user, smtp_pass)
            except smtplib.SMTPNotSupportedError:
                # 서버가 인증을 요구하지 않거나 지원하지 않는 경우 무시
                pass
        smtp.send_message(msg)

    return {"status": "sent", "to": to_email}