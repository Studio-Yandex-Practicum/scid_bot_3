from aiogram.types import Message


def get_user_id(message: Message) -> int:
    """Получает ID пользователя из сообщения."""

    return message.from_user.id
