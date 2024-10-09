# Отправка уведомления на почту для менеджеров

import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from aiosmtplib import SMTP
from dotenv import load_dotenv

load_dotenv()

BASE_EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")


async def send_mail(subject, to, user_data):
    text = (f'Пользователь {user_data["first_name"]} '
            f'заказал звонок по номеру {user_data["phone_number"]}')

    message = MIMEMultipart()
    message["From"] = BASE_EMAIL
    message["To"] = to
    message["Subject"] = subject
    message.attach(
        MIMEText(f"<html><body>{text}</body></html>", "html", "utf-8"))

    smtp_client = SMTP(hostname="smtp.yandex.ru", port=465, use_tls=True)
    async with smtp_client:
        await smtp_client.login(BASE_EMAIL, PASSWORD)
        await smtp_client.send_message(message)
