import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования
logger = logging.getLogger(__name__)

bot = Bot(token=os.getenv('BOT_TOKEN'))
dispatcher = Dispatcher(storage=MemoryStorage())


def check_token() -> None:
    """Проверка наличия токена бота."""

    if os.getenv('BOT_TOKEN') is None:
        logger.error("Токен бота не найден.")
        raise ValueError('Отсутствуют необходимые токены.')

    else:
        logger.info("Токен бота успешно загружен.")
