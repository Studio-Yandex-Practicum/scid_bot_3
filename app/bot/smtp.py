from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aiosmtplib import SMTP

from core.settings import settings


async def send_mail(subject, to, user_data):
    text = (
        f'Пользователь {user_data["first_name"]} '
        f'заказал звонок по номеру {user_data["phone_number"]}'
    )

    message = MIMEMultipart()
    message["From"] = settings.email
    message["To"] = to
    message["Subject"] = subject
    message.attach(
        MIMEText(f"<html><body>{text}</body></html>", "html", "utf-8")
    )

    smtp_client = SMTP(hostname="smtp.yandex.ru", port=465, use_tls=True)
    async with smtp_client:
        await smtp_client.login(settings.email, settings.email_password)
        await smtp_client.send_message(message)
