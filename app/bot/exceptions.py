import logging
from functools import wraps
from typing import Callable

from aiogram.types import Message


logger = logging.getLogger(__name__)


def message_exception_handler(
    log_error_text: str,
    message_error_text: str = 'Произошла ошибка. Пожалуйста, попробуйте позже.'
) -> Callable:
    """Обработчик ошибок."""

    def decorator(coroutine: Callable):
        @wraps(coroutine)
        async def wrapper(*args, **kwargs) -> None:
            try:
                await coroutine(*args, **kwargs)
            except Exception as e:
                message: Message = args[0] if args else None

                if message:
                    await message.answer(message_error_text)

                logger.error(f"{log_error_text} {e}")

        return wrapper

    return decorator
