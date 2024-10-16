import re

from admin.admin_settings import PHONE_NUMBER_REGEX


def phone_number_validator(phone_number: int) -> bool:
    """Вовзращает True если номер телефона соответствует шаблону."""
    phone_number = re.sub(r"[-()./ ]", "", phone_number)
    return re.match(PHONE_NUMBER_REGEX, phone_number) is not None


def validate_url(url: str):
    """Валидация ссылки."""
    regex = re.compile(
        r'^(https://)'
        r'([A-Za-z0-9.-]+)'  # Домен
        r'(:\d+)?'  # Порт (необязательный)
        r'(/.*)?$'  # Путь (необязательный)
    )
    return re.match(regex, url) is not None
