import smtplib
from email.message import EmailMessage

from src.config.env import (
    SMTP_FROM_EMAIL,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_STARTTLS,
    SMTP_USERNAME,
)


class MailerConfigurationError(RuntimeError):
    pass


def send_email(to_email: str, subject: str, plain_text_body: str, html_body: str | None = None) -> None:
    if not SMTP_HOST or not SMTP_FROM_EMAIL:
        raise MailerConfigurationError("SMTP_HOST and SMTP_FROM_EMAIL must be configured")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = SMTP_FROM_EMAIL
    message["To"] = to_email
    message.set_content(plain_text_body)

    if html_body:
        message.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        if SMTP_STARTTLS:
            smtp.starttls()
        if SMTP_USERNAME and SMTP_PASSWORD:
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        smtp.send_message(message)
