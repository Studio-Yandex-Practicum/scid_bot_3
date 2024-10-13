from aiogram.types import Message
import re


def get_user_id(message: Message) -> int:
    """Получает ID пользователя из сообщения."""
    return message.from_user.id


def is_valid_name(name: str) -> bool:
    """Проверяет, что имя содержит только буквы."""
    return bool(re.match(r'^[a-zA-Zа-яА-ЯёЁ]+$', name))


def is_valid_phone_number(phone_number: str) -> bool:
    """Проверяет, что номер телефона соответствует шаблону +7XXXXXXXXXX или 8XXXXXXXXXX."""
    return bool(re.match(r'^(\+7|8)\d{10}$', phone_number))
