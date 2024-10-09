import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from .settings import settings

logger = logging.getLogger(__name__)

bot = Bot(token=settings.bot_token)
dispatcher = Dispatcher(storage=MemoryStorage())


def check_token() -> None:
    """Проверка наличия токена бота."""

    if settings.bot_token is None:
        logger.error("Токен бота не найден.")
        raise ValueError('Отсутствуют необходимые токены.')
    else:
        logger.info("Токен бота успешно загружен.")
