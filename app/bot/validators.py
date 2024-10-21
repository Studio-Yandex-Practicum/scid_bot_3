from re import match


def is_valid_name(name: str) -> bool:
    """Проверяет, что имя содержит только буквы."""

    return bool(match(r"^[A-Za-zА-Яа-яЁё ]+$", name))


def is_valid_phone_number(phone_number: str) -> bool:
    """
    Валидация номера телефона.

    Проверяет, что номер телефона соответствует
    шаблону +7XXXXXXXXXX или 8XXXXXXXXXX.
    """

    return bool(match(r"^(\+7|8)\d{10}$", phone_number))


def format_phone_number(phone_number: str) -> str:
    """Преобразует номер телефона, начинающийся с 8, в формат +7."""

    if phone_number.startswith("8"):
        return "+7" + phone_number[1:]

    return phone_number


def is_valid_rating(rating: str) -> bool:
    """Валидация рейтинга от 1 до 10."""

    return rating.isdigit() and (1 <= int(rating) <= 10)
