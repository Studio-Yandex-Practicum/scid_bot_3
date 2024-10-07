import re

from settings import PHONE_NUMBER_REGEX


def phone_number_validator(phone_number: int) -> bool:
    """Вовзращает True если номер телефона соответствует шаблону."""
    phone_number = re.sub(r"[-()./ ]", "", phone_number)
    return re.match(PHONE_NUMBER_REGEX, phone_number) is not None
